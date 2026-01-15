"""
Swig Synthetic Data Generator
Generates 3 weeks of realistic operational data for GM AI Agent training.
"""

import duckdb
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from faker import Faker
from tqdm import tqdm
import yaml

# Local imports
from utils.swig_pulse import SwigPulse, get_time_period, simulate_queue_position
from utils.dirty_soda_combinator import DirtySodaCombinator, generate_vehicle_descriptor


class SwigDataGenerator:
    """Main orchestrator for synthetic data generation."""

    def __init__(
        self,
        db_path: str = 'swig_operations.duckdb',
        start_date: date = None,
        num_days: int = 21,
        seed: int = 42
    ):
        self.db_path = db_path
        self.start_date = start_date or date(2025, 1, 6)  # Start on a Monday
        self.num_days = num_days
        self.seed = seed

        np.random.seed(seed)
        self.faker = Faker()
        Faker.seed(seed)

        self.pulse = SwigPulse(seed=seed)
        self.combinator = DirtySodaCombinator(seed=seed)

        # Config paths
        self.sql_dir = Path(__file__).parent / 'sql'
        self.config_dir = Path(__file__).parent / 'config'

        # Load probability config
        with open(self.config_dir / 'probability_tables.yaml', 'r') as f:
            self.config = yaml.safe_load(f)

        # Store IDs
        self.store_ids = [1001, 1002, 1003]

        # Runtime state
        self.conn = None
        self.employees = {}  # store_id -> list of employee dicts
        self.inventory_state = {}  # (store_id, inventory_id) -> current_balance

    def setup_database(self):
        """Create database and execute schema."""
        print("Setting up DuckDB database...")

        # Remove existing database
        db_file = Path(self.db_path)
        if db_file.exists():
            db_file.unlink()

        self.conn = duckdb.connect(self.db_path)

        # Execute schema SQL - read and process line by line
        schema_sql = (self.sql_dir / '01_create_tables.sql').read_text()

        # Remove comment lines and build statements
        lines = []
        for line in schema_sql.split('\n'):
            stripped = line.strip()
            if stripped.startswith('--'):
                continue  # Skip comment lines
            lines.append(line)

        clean_sql = '\n'.join(lines)

        # Split by semicolon and execute
        for statement in clean_sql.split(';'):
            statement = statement.strip()
            if statement:
                try:
                    self.conn.execute(statement)
                except Exception as e:
                    if 'already exists' not in str(e).lower():
                        print(f"Schema warning: {e}")

        # Execute seed data SQL
        print("Loading seed data...")
        seed_sql = (self.sql_dir / '02_seed_reference_data.sql').read_text()

        # Remove comment lines
        lines = []
        for line in seed_sql.split('\n'):
            stripped = line.strip()
            if stripped.startswith('--'):
                continue
            lines.append(line)

        clean_sql = '\n'.join(lines)

        for statement in clean_sql.split(';'):
            statement = statement.strip()
            if statement:
                try:
                    self.conn.execute(statement)
                except Exception as e:
                    print(f"Seed data warning: {e}")

        print("Database setup complete!")

    def generate_employees(self):
        """Generate employees for all stores."""
        print("Generating employees...")

        roles_distribution = {
            'GM': 1,
            'ASM': 2,
            'SHIFT': 3,
            'MIX': 8,
            'RUNNER': 6,
            'TRAIN': 2
        }

        employee_id = 1000

        for store_id in self.store_ids:
            self.employees[store_id] = []

            for role, count in roles_distribution.items():
                for _ in range(count):
                    employee_id += 1

                    # Determine age - minors for RUNNER and TRAIN roles
                    if role in ['RUNNER', 'TRAIN']:
                        age = int(np.random.choice([16, 17, 18, 19], p=[0.3, 0.3, 0.25, 0.15]))
                    else:
                        age = int(np.random.randint(18, 45))

                    dob = date.today() - timedelta(days=int(age * 365 + np.random.randint(0, 365)))
                    is_minor = age < 18

                    # Hire date - longer tenure for managers
                    if role == 'GM':
                        tenure_days = int(np.random.randint(365, 1095))  # 1-3 years
                    elif role in ['ASM', 'SHIFT']:
                        tenure_days = int(np.random.randint(180, 730))  # 6mo-2yr
                    else:
                        tenure_days = int(np.random.randint(30, 365))  # 1mo-1yr

                    hire_date = date.today() - timedelta(days=tenure_days)

                    # Wage based on role
                    base_wages = {'GM': 22, 'ASM': 17, 'SHIFT': 14.5, 'MIX': 12, 'RUNNER': 11.5, 'TRAIN': 11}
                    wage = base_wages[role] + np.random.uniform(-0.5, 1.0)

                    emp = {
                        'Employee_ID': employee_id,
                        'Store_ID': store_id,
                        'Harri_UID': str(uuid.uuid4()),
                        'First_Name': self.faker.first_name(),
                        'Last_Name': self.faker.last_name(),
                        'Role_Code': role,
                        'Hire_Date': hire_date,
                        'Date_of_Birth': dob,
                        'Is_Minor': is_minor,
                        'Hourly_Wage': round(wage, 2),
                        'Email': f"{self.faker.user_name()}@email.com",
                        'Phone': self.faker.phone_number()[:12],
                        'Food_Handler_Exp': date.today() + timedelta(days=int(np.random.randint(30, 365))),
                        'Status': 'Active'
                    }

                    self.employees[store_id].append(emp)

                    # Insert into database
                    self.conn.execute("""
                        INSERT INTO Employee_Master_Profile VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, [
                        emp['Employee_ID'], emp['Store_ID'], emp['Harri_UID'],
                        emp['First_Name'], emp['Last_Name'], emp['Role_Code'],
                        emp['Hire_Date'], emp['Date_of_Birth'], emp['Is_Minor'],
                        emp['Hourly_Wage'], emp['Email'], emp['Phone'],
                        emp['Food_Handler_Exp'], emp['Status']
                    ])

        total_employees = sum(len(emps) for emps in self.employees.values())
        print(f"Generated {total_employees} employees across {len(self.store_ids)} stores")

    def generate_loyalty_profiles(self, num_profiles: int = 2000):
        """Generate loyalty program members."""
        print(f"Generating {num_profiles} loyalty profiles...")

        for _ in range(num_profiles):
            join_days_ago = int(np.random.randint(1, 730))
            join_date = date.today() - timedelta(days=join_days_ago)
            visits = int(np.random.exponential(15))  # Most have few visits, some have many
            lifetime_spend = visits * np.random.uniform(5, 12)

            self.conn.execute("""
                INSERT INTO Loyalty_Profiles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                str(uuid.uuid4()),
                self.faker.first_name(),
                self.faker.phone_number()[-4:],
                self.faker.free_email().split('@')[1],
                join_date,
                int(lifetime_spend * 10),  # Points
                round(lifetime_spend, 2),
                visits,
                int(np.random.choice(self.store_ids)),
                date.today() - timedelta(days=int(np.random.randint(0, 30)))
            ])

    def generate_schedule_for_day(self, store_id: int, shift_date: date) -> List[Dict]:
        """Generate shift schedule for a single day at a store."""
        schedules = []
        is_weekend = shift_date.weekday() >= 5

        # Determine staffing needs by shift
        if is_weekend:
            shifts_needed = {
                'opening': {'MIX': 2, 'RUNNER': 2, 'SHIFT': 1},      # 6am-2pm
                'mid': {'MIX': 3, 'RUNNER': 3, 'SHIFT': 1, 'ASM': 1},  # 10am-6pm
                'closing': {'MIX': 2, 'RUNNER': 2, 'SHIFT': 1},       # 2pm-10pm
            }
        else:
            shifts_needed = {
                'opening': {'MIX': 2, 'RUNNER': 1, 'SHIFT': 1},
                'mid': {'MIX': 4, 'RUNNER': 4, 'SHIFT': 1, 'ASM': 1},  # Peak coverage
                'closing': {'MIX': 2, 'RUNNER': 2, 'SHIFT': 1},
            }

        shift_times = {
            'opening': (6, 14),   # 6am-2pm
            'mid': (10, 18),      # 10am-6pm
            'closing': (14, 22),  # 2pm-10pm
        }

        store_employees = self.employees[store_id]

        for shift_name, roles_needed in shifts_needed.items():
            start_hour, end_hour = shift_times[shift_name]

            for role, count in roles_needed.items():
                # Find available employees with this role
                eligible = [e for e in store_employees if e['Role_Code'] == role]

                # Select employees (with some randomness)
                selected = np.random.choice(
                    eligible,
                    size=min(count, len(eligible)),
                    replace=False
                ).tolist() if eligible else []

                for emp in selected:
                    schedule = {
                        'Schedule_UUID': str(uuid.uuid4()),
                        'Store_ID': store_id,
                        'Employee_ID': emp['Employee_ID'],
                        'Shift_Date': shift_date,
                        'Shift_Start': datetime.combine(shift_date, datetime.min.time().replace(hour=start_hour)),
                        'Shift_End': datetime.combine(shift_date, datetime.min.time().replace(hour=end_hour)),
                        'Scheduled_Hours': end_hour - start_hour,
                        'Job_Role': role,
                        'Is_Posted': True,
                        'Forecast_Sales': np.random.uniform(3000, 6000) if shift_name == 'mid' else np.random.uniform(1500, 3000)
                    }
                    schedules.append(schedule)

        return schedules

    def generate_attendance_for_schedule(self, schedule: Dict) -> Dict:
        """Generate actual attendance record for a scheduled shift."""
        # 5% no-show rate
        is_no_show = np.random.random() < 0.05

        if is_no_show:
            return {
                'Punch_UUID': str(uuid.uuid4()),
                'Store_ID': schedule['Store_ID'],
                'Employee_ID': schedule['Employee_ID'],
                'Schedule_UUID': schedule['Schedule_UUID'],
                'Shift_Date': schedule['Shift_Date'],
                'Clock_In_Time': None,
                'Clock_Out_Time': None,
                'Break_Start': None,
                'Break_End': None,
                'Break_Duration_Minutes': None,
                'Actual_Hours': 0,
                'Validation_Method': None,
                'Is_Late': False,
                'Late_Minutes': 0,
                'Is_No_Show': True
            }

        # Clock in with some variance (-5 to +15 minutes)
        clock_in_variance = np.random.normal(2, 5)  # Average 2 min late
        clock_in_variance = max(-5, min(15, clock_in_variance))  # Clamp

        clock_in = schedule['Shift_Start'] + timedelta(minutes=clock_in_variance)
        is_late = clock_in_variance > 5  # Late if more than 5 min after start
        late_minutes = max(0, int(clock_in_variance - 5))

        # Clock out with some variance (-10 to +30 minutes)
        clock_out_variance = np.random.normal(5, 10)  # Often stay a bit late
        clock_out = schedule['Shift_End'] + timedelta(minutes=clock_out_variance)

        # Break for shifts > 5 hours
        scheduled_hours = schedule['Scheduled_Hours']
        break_start = None
        break_end = None
        break_duration = 0

        if scheduled_hours >= 5:
            # 90% take their break
            if np.random.random() < 0.90:
                break_midpoint = clock_in + timedelta(hours=scheduled_hours / 2)
                break_start = break_midpoint - timedelta(minutes=np.random.randint(0, 30))
                break_duration = 30 if scheduled_hours >= 6 else 15
                break_end = break_start + timedelta(minutes=break_duration)

        actual_hours = (clock_out - clock_in).total_seconds() / 3600
        if break_duration:
            actual_hours -= break_duration / 60

        # Validation method
        validation = np.random.choice(
            ['Biometric', 'Pin', 'Manager_Override'],
            p=[0.85, 0.12, 0.03]
        )

        return {
            'Punch_UUID': str(uuid.uuid4()),
            'Store_ID': schedule['Store_ID'],
            'Employee_ID': schedule['Employee_ID'],
            'Schedule_UUID': schedule['Schedule_UUID'],
            'Shift_Date': schedule['Shift_Date'],
            'Clock_In_Time': clock_in,
            'Clock_Out_Time': clock_out,
            'Break_Start': break_start,
            'Break_End': break_end,
            'Break_Duration_Minutes': break_duration if break_duration else None,
            'Actual_Hours': round(actual_hours, 2),
            'Validation_Method': validation,
            'Is_Late': is_late,
            'Late_Minutes': late_minutes,
            'Is_No_Show': False
        }

    def check_compliance_violations(self, attendance: Dict, employee: Dict) -> List[Dict]:
        """Check for labor compliance violations."""
        violations = []

        if attendance['Is_No_Show']:
            return violations

        # Check minor violations
        if employee['Is_Minor']:
            # Minor working past 9:30pm
            if attendance['Clock_Out_Time'] and attendance['Clock_Out_Time'].hour >= 22:
                violations.append({
                    'Violation_UUID': str(uuid.uuid4()),
                    'Store_ID': attendance['Store_ID'],
                    'Employee_ID': attendance['Employee_ID'],
                    'Punch_UUID': attendance['Punch_UUID'],
                    'Violation_Date': attendance['Shift_Date'],
                    'Violation_Type': 'Minor_Late_Hours',
                    'Description': f"Minor worked past 9:30pm ({attendance['Clock_Out_Time'].strftime('%I:%M %p')})",
                    'Penalty_Cost': 100.00,
                    'Manager_Ack': False,
                    'Resolved': False
                })

            # Minor overtime (>4 hours on school day, >8 on non-school)
            if attendance['Actual_Hours'] and attendance['Actual_Hours'] > 8:
                violations.append({
                    'Violation_UUID': str(uuid.uuid4()),
                    'Store_ID': attendance['Store_ID'],
                    'Employee_ID': attendance['Employee_ID'],
                    'Punch_UUID': attendance['Punch_UUID'],
                    'Violation_Date': attendance['Shift_Date'],
                    'Violation_Type': 'Minor_Overtime',
                    'Description': f"Minor worked {attendance['Actual_Hours']:.1f} hours (>8 limit)",
                    'Penalty_Cost': 50.00,
                    'Manager_Ack': False,
                    'Resolved': False
                })

        # Missed break (shift > 5 hours, no break)
        if attendance['Actual_Hours'] and attendance['Actual_Hours'] >= 5:
            if not attendance['Break_Start']:
                violations.append({
                    'Violation_UUID': str(uuid.uuid4()),
                    'Store_ID': attendance['Store_ID'],
                    'Employee_ID': attendance['Employee_ID'],
                    'Punch_UUID': attendance['Punch_UUID'],
                    'Violation_Date': attendance['Shift_Date'],
                    'Violation_Type': 'Missed_Break',
                    'Description': f"No break taken during {attendance['Actual_Hours']:.1f} hour shift",
                    'Penalty_Cost': 50.00,
                    'Manager_Ack': False,
                    'Resolved': False
                })

        return violations

    def generate_transactions_for_day(
        self,
        store_id: int,
        business_date: date,
        employees_on_shift: List[Dict]
    ):
        """Generate all transactions for a single day at a store."""
        # Generate order timestamps using Swig Pulse
        is_weekend = business_date.weekday() >= 5
        timestamps = self.pulse.generate_daily_timestamps(
            datetime.combine(business_date, datetime.min.time()),
            base_volume=1000 if not is_weekend else 800,
            is_weekend=is_weekend
        )

        # Get loyalty IDs for potential linking
        loyalty_ids = self.conn.execute(
            "SELECT Customer_Loyalty_ID FROM Loyalty_Profiles"
        ).fetchall()
        loyalty_ids = [l[0] for l in loyalty_ids]

        transactions_batch = []
        line_items_batch = []
        payments_batch = []
        loop_metrics_batch = []

        for timestamp in timestamps:
            time_period = get_time_period(timestamp)
            if time_period == 'closed':
                continue

            # Select employee for this order
            eligible_employees = [e for e in employees_on_shift if e['Role_Code'] in ['MIX', 'RUNNER', 'SHIFT']]
            if not eligible_employees:
                continue
            employee = np.random.choice(eligible_employees)

            # Generate order
            order_items = self.combinator.generate_order(time_period)
            if not order_items:
                continue

            subtotal, tax, total = self.combinator.calculate_order_total(order_items)

            # Determine service channel
            is_weekend = business_date.weekday() >= 5
            channel_key = 'weekend' if is_weekend else 'weekday'
            channel_probs = self.config['service_channel_probabilities'][channel_key]
            service_channel = np.random.choice(
                list(channel_probs.keys()),
                p=list(channel_probs.values())
            )

            # Queue position (only for drive-thru)
            queue_pos = simulate_queue_position(timestamp) if service_channel == 'Drive_Thru' else 0
            vehicle = generate_vehicle_descriptor() if service_channel == 'Drive_Thru' else None

            # Order device
            if service_channel == 'Drive_Thru' and queue_pos > 2:
                device = f"Tablet_LB_{np.random.randint(1, 5):02d}"
            else:
                device = f"Window_POS_{np.random.randint(1, 3):02d}"

            # Loyalty linking
            customer_loyalty_id = None
            if np.random.random() < self.config['loyalty_rates']['identified_rate']:
                customer_loyalty_id = np.random.choice(loyalty_ids)

            # Apply discount (10% of orders)
            discount = 0
            if np.random.random() < 0.10:
                discount = round(subtotal * np.random.uniform(0.10, 0.20), 2)
                total = round(total - discount, 2)

            # Fulfillment time (3-12 minutes depending on queue)
            fulfillment_minutes = 3 + queue_pos * 0.5 + np.random.uniform(0, 3)
            close_timestamp = timestamp + timedelta(minutes=fulfillment_minutes)

            transaction_uuid = str(uuid.uuid4())

            transactions_batch.append({
                'Transaction_UUID': transaction_uuid,
                'Store_ID': store_id,
                'Business_Date': business_date,
                'Open_Timestamp': timestamp,
                'Close_Timestamp': close_timestamp,
                'Service_Channel': service_channel,
                'Order_Source_Device': device,
                'Employee_ID': employee['Employee_ID'],
                'Customer_Loyalty_ID': customer_loyalty_id,
                'Queue_Position': queue_pos,
                'Vehicle_Descriptor': vehicle,
                'Subtotal_Amount': round(subtotal, 2),
                'Tax_Amount': round(tax, 2),
                'Discount_Total': discount,
                'Total_Amount': round(total, 2),
                'Is_Voided': False
            })

            # Line items
            parent_line_uuid = None
            for item in order_items:
                line_uuid = str(uuid.uuid4())

                if item.item_type == 'Base_Beverage':
                    parent_line_uuid = line_uuid

                line_items_batch.append({
                    'Line_Item_UUID': line_uuid,
                    'Transaction_UUID': transaction_uuid,
                    'Item_SKU': item.sku,
                    'Item_Name': item.name,
                    'Item_Type': item.item_type,
                    'Quantity': item.quantity,
                    'Unit_Price': item.unit_price,
                    'Line_Total': round(item.unit_price * item.quantity, 2),
                    'Parent_Line_UUID': parent_line_uuid if item.parent_sku else None,
                    'Modifier_Group': item.modifier_group,
                    'Price_Override': None,
                    'Is_Comped': False
                })

            # Payment
            payment_probs = self.config['payment_type_probabilities']
            tender_type = np.random.choice(
                list(payment_probs.keys()),
                p=list(payment_probs.values())
            )

            # Tips for card payments
            tip = 0
            if tender_type in ['Credit_Card', 'Debit_Card', 'Apple_Pay', 'Google_Pay']:
                if np.random.random() < self.config['tip_behavior']['probability']:
                    tip_dist = self.config['tip_behavior']['distribution']
                    tip_values = [float(k.replace('$', '')) if k != 'other' else np.random.uniform(1, 10)
                                  for k in tip_dist.keys()]
                    tip_probs = list(tip_dist.values())
                    tip = round(np.random.choice(tip_values, p=tip_probs), 2)

            payments_batch.append({
                'Payment_UUID': str(uuid.uuid4()),
                'Transaction_UUID': transaction_uuid,
                'Tender_Type': tender_type,
                'Amount_Tendered': round(total + tip, 2),
                'Tip_Amount': tip,
                'Change_Given': 0,
                'Auth_Code': self.faker.bothify(text='???###') if tender_type != 'Cash' else None,
                'Masked_PAN': self.faker.credit_card_number()[-4:] if 'Card' in tender_type else None,
                'Payment_Timestamp': close_timestamp,
                'Is_Refund': False
            })

            # Drive-thru loop metrics
            if service_channel == 'Drive_Thru':
                entry_time = timestamp - timedelta(minutes=queue_pos * 0.8)
                loop_metrics_batch.append({
                    'Loop_Event_UUID': str(uuid.uuid4()),
                    'Store_ID': store_id,
                    'Transaction_UUID': transaction_uuid,
                    'Sensor_ID': 'Window',
                    'Arrival_Time': timestamp,
                    'Departure_Time': close_timestamp,
                    'Duration_Seconds': int((close_timestamp - timestamp).total_seconds()),
                    'Car_Count_Hour': len([t for t in timestamps
                                           if timestamp - timedelta(hours=1) <= t <= timestamp]),
                    'Business_Date': business_date
                })

        return transactions_batch, line_items_batch, payments_batch, loop_metrics_batch

    def run(self):
        """Execute the full data generation pipeline."""
        print("=" * 60)
        print("SWIG SYNTHETIC DATA GENERATOR")
        print("=" * 60)
        print(f"Database: {self.db_path}")
        print(f"Date Range: {self.start_date} to {self.start_date + timedelta(days=self.num_days - 1)}")
        print(f"Stores: {self.store_ids}")
        print("=" * 60)

        # Setup
        self.setup_database()
        self.generate_employees()
        self.generate_loyalty_profiles()

        # Generate data day by day
        print("\nGenerating daily operational data...")

        total_transactions = 0
        total_schedules = 0
        total_violations = 0

        for day_offset in tqdm(range(self.num_days), desc="Days"):
            current_date = self.start_date + timedelta(days=day_offset)

            for store_id in self.store_ids:
                # Generate schedules
                schedules = self.generate_schedule_for_day(store_id, current_date)
                total_schedules += len(schedules)

                for schedule in schedules:
                    self.conn.execute("""
                        INSERT INTO Labor_Schedules_Published VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, [
                        schedule['Schedule_UUID'], schedule['Store_ID'], schedule['Employee_ID'],
                        schedule['Shift_Date'], schedule['Shift_Start'], schedule['Shift_End'],
                        schedule['Scheduled_Hours'], schedule['Job_Role'], schedule['Is_Posted'],
                        schedule['Forecast_Sales']
                    ])

                # Generate attendance
                employees_on_shift = []
                for schedule in schedules:
                    emp = next((e for e in self.employees[store_id]
                               if e['Employee_ID'] == schedule['Employee_ID']), None)
                    if emp:
                        employees_on_shift.append(emp)

                    attendance = self.generate_attendance_for_schedule(schedule)
                    self.conn.execute("""
                        INSERT INTO Time_Attendance_Actuals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, [
                        attendance['Punch_UUID'], attendance['Store_ID'], attendance['Employee_ID'],
                        attendance['Schedule_UUID'], attendance['Shift_Date'], attendance['Clock_In_Time'],
                        attendance['Clock_Out_Time'], attendance['Break_Start'], attendance['Break_End'],
                        attendance['Break_Duration_Minutes'], attendance['Actual_Hours'],
                        attendance['Validation_Method'], attendance['Is_Late'], attendance['Late_Minutes'],
                        attendance['Is_No_Show']
                    ])

                    # Check for violations
                    if emp:
                        violations = self.check_compliance_violations(attendance, emp)
                        for violation in violations:
                            total_violations += 1
                            self.conn.execute("""
                                INSERT INTO Labor_Compliance_Violations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, [
                                violation['Violation_UUID'], violation['Store_ID'], violation['Employee_ID'],
                                violation['Punch_UUID'], violation['Violation_Date'], violation['Violation_Type'],
                                violation['Description'], violation['Penalty_Cost'], violation['Manager_Ack'],
                                violation['Resolved']
                            ])

                # Generate transactions
                transactions, line_items, payments, loop_metrics = self.generate_transactions_for_day(
                    store_id, current_date, employees_on_shift
                )
                total_transactions += len(transactions)

                # Batch insert transactions
                for tx in transactions:
                    self.conn.execute("""
                        INSERT INTO Sales_Transactions_Header VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, list(tx.values()))

                for item in line_items:
                    self.conn.execute("""
                        INSERT INTO Sales_Order_Line_Items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, list(item.values()))

                for payment in payments:
                    self.conn.execute("""
                        INSERT INTO Sales_Payments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, list(payment.values()))

                for metric in loop_metrics:
                    self.conn.execute("""
                        INSERT INTO Drive_Thru_Loop_Metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, list(metric.values()))

        # Final summary
        print("\n" + "=" * 60)
        print("GENERATION COMPLETE!")
        print("=" * 60)
        print(f"Total Transactions: {total_transactions:,}")
        print(f"Total Schedules: {total_schedules:,}")
        print(f"Total Violations: {total_violations:,}")

        # Verify counts
        tx_count = self.conn.execute("SELECT COUNT(*) FROM Sales_Transactions_Header").fetchone()[0]
        emp_count = self.conn.execute("SELECT COUNT(*) FROM Employee_Master_Profile").fetchone()[0]
        line_count = self.conn.execute("SELECT COUNT(*) FROM Sales_Order_Line_Items").fetchone()[0]

        print(f"\nDatabase Verification:")
        print(f"  - Transactions in DB: {tx_count:,}")
        print(f"  - Employees in DB: {emp_count:,}")
        print(f"  - Line Items in DB: {line_count:,}")

        self.conn.close()
        print(f"\nDatabase saved to: {self.db_path}")


if __name__ == '__main__':
    generator = SwigDataGenerator(
        db_path='swig_operations.duckdb',
        start_date=date(2025, 1, 6),  # Start on a Monday
        num_days=21,  # 3 weeks
        seed=42
    )
    generator.run()
