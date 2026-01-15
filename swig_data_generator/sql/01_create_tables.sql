-- Swig Operations Database Schema
-- DuckDB-compatible DDL for all 20 tables
-- Generated for GM AI Agent training data

-- =============================================================================
-- REFERENCE/CONFIGURATION TABLES
-- =============================================================================

-- 1. Organization_Stores - Store master data
CREATE TABLE IF NOT EXISTS Organization_Stores (
    Store_ID INTEGER PRIMARY KEY,
    Store_Name VARCHAR(100) NOT NULL,
    Address VARCHAR(255),
    City VARCHAR(50),
    State VARCHAR(2),
    Zip VARCHAR(10),
    Latitude DECIMAL(9,6),
    Longitude DECIMAL(9,6),
    Timezone VARCHAR(50) DEFAULT 'America/Denver',
    Open_Time TIME DEFAULT '06:00:00',
    Close_Time TIME DEFAULT '22:00:00',
    Is_Active BOOLEAN DEFAULT true,
    Open_Date DATE
);

-- 2. Product_Categories - Item categorization
CREATE TABLE IF NOT EXISTS Product_Categories (
    Category_ID INTEGER PRIMARY KEY,
    Category_Name VARCHAR(50) NOT NULL,
    Display_Order INTEGER
);

-- 3. Product_Catalog - Menu items and SKUs
CREATE TABLE IF NOT EXISTS Product_Catalog (
    Item_SKU VARCHAR(20) PRIMARY KEY,
    Item_Name VARCHAR(100) NOT NULL,
    Category_ID INTEGER REFERENCES Product_Categories(Category_ID),
    Item_Type VARCHAR(20) CHECK (Item_Type IN ('Base_Beverage', 'Modifier', 'Food', 'Merch')),
    Base_Price DECIMAL(6,2) NOT NULL,
    Is_Available BOOLEAN DEFAULT true,
    Calories INTEGER,
    Size_Oz INTEGER,
    Is_Sugar_Free BOOLEAN DEFAULT false,
    Description VARCHAR(255)
);

-- 4. Vendors - Supplier information
CREATE TABLE IF NOT EXISTS Vendors (
    Vendor_ID INTEGER PRIMARY KEY,
    Vendor_Name VARCHAR(100) NOT NULL,
    Contact_Name VARCHAR(100),
    Contact_Email VARCHAR(100),
    Contact_Phone VARCHAR(20),
    Lead_Time_Days INTEGER DEFAULT 3,
    Is_Active BOOLEAN DEFAULT true
);

-- 5. Job_Roles - Position definitions
CREATE TABLE IF NOT EXISTS Job_Roles (
    Role_Code VARCHAR(20) PRIMARY KEY,
    Role_Name VARCHAR(50) NOT NULL,
    Base_Hourly_Rate DECIMAL(5,2),
    Can_Manage BOOLEAN DEFAULT false,
    Can_Handle_Cash BOOLEAN DEFAULT true,
    Min_Age INTEGER DEFAULT 16
);

-- 6. Loyalty_Profiles - Customer data
CREATE TABLE IF NOT EXISTS Loyalty_Profiles (
    Customer_Loyalty_ID VARCHAR(36) PRIMARY KEY,  -- UUID as string
    First_Name VARCHAR(50),
    Phone_Last4 VARCHAR(4),
    Email_Domain VARCHAR(50),
    Join_Date DATE,
    Points_Balance INTEGER DEFAULT 0,
    Lifetime_Spend DECIMAL(10,2) DEFAULT 0,
    Visit_Count INTEGER DEFAULT 0,
    Preferred_Store_ID INTEGER REFERENCES Organization_Stores(Store_ID),
    Last_Visit_Date DATE
);

-- =============================================================================
-- POS TABLES (Crisp Ecosystem)
-- =============================================================================

-- 7. Sales_Transactions_Header - Transaction parent records
CREATE TABLE IF NOT EXISTS Sales_Transactions_Header (
    Transaction_UUID VARCHAR(36) PRIMARY KEY,
    Store_ID INTEGER NOT NULL REFERENCES Organization_Stores(Store_ID),
    Business_Date DATE NOT NULL,
    Open_Timestamp TIMESTAMP NOT NULL,
    Close_Timestamp TIMESTAMP,
    Service_Channel VARCHAR(20) CHECK (Service_Channel IN ('Drive_Thru', 'Walk_Up', 'Mobile_Pickup', 'Delivery_3rdParty')),
    Order_Source_Device VARCHAR(50),
    Employee_ID INTEGER,
    Customer_Loyalty_ID VARCHAR(36) REFERENCES Loyalty_Profiles(Customer_Loyalty_ID),
    Queue_Position INTEGER,
    Vehicle_Descriptor VARCHAR(100),
    Subtotal_Amount DECIMAL(10,2),
    Tax_Amount DECIMAL(10,2),
    Discount_Total DECIMAL(10,2) DEFAULT 0,
    Total_Amount DECIMAL(10,2),
    Is_Voided BOOLEAN DEFAULT false
);

-- 8. Sales_Order_Line_Items - Items per transaction
CREATE TABLE IF NOT EXISTS Sales_Order_Line_Items (
    Line_Item_UUID VARCHAR(36) PRIMARY KEY,
    Transaction_UUID VARCHAR(36) NOT NULL REFERENCES Sales_Transactions_Header(Transaction_UUID),
    Item_SKU VARCHAR(20) REFERENCES Product_Catalog(Item_SKU),
    Item_Name VARCHAR(100),
    Item_Type VARCHAR(20) CHECK (Item_Type IN ('Base_Beverage', 'Modifier', 'Food', 'Merch')),
    Quantity INTEGER DEFAULT 1,
    Unit_Price DECIMAL(6,2),
    Line_Total DECIMAL(8,2),
    Parent_Line_UUID VARCHAR(36),  -- Self-reference for modifiers
    Modifier_Group VARCHAR(50),
    Price_Override DECIMAL(6,2),
    Is_Comped BOOLEAN DEFAULT false
);

-- 9. Sales_Payments - Payment details
CREATE TABLE IF NOT EXISTS Sales_Payments (
    Payment_UUID VARCHAR(36) PRIMARY KEY,
    Transaction_UUID VARCHAR(36) NOT NULL REFERENCES Sales_Transactions_Header(Transaction_UUID),
    Tender_Type VARCHAR(20) CHECK (Tender_Type IN ('Credit_Card', 'Debit_Card', 'Cash', 'Apple_Pay', 'Google_Pay', 'Swig_Gift_Card', 'Loyalty_Points')),
    Amount_Tendered DECIMAL(10,2) NOT NULL,
    Tip_Amount DECIMAL(6,2) DEFAULT 0,
    Change_Given DECIMAL(6,2) DEFAULT 0,
    Auth_Code VARCHAR(20),
    Masked_PAN VARCHAR(4),
    Payment_Timestamp TIMESTAMP,
    Is_Refund BOOLEAN DEFAULT false
);

-- 10. Drive_Thru_Loop_Metrics - Car sensor data
CREATE TABLE IF NOT EXISTS Drive_Thru_Loop_Metrics (
    Loop_Event_UUID VARCHAR(36) PRIMARY KEY,
    Store_ID INTEGER NOT NULL REFERENCES Organization_Stores(Store_ID),
    Transaction_UUID VARCHAR(36) REFERENCES Sales_Transactions_Header(Transaction_UUID),
    Sensor_ID VARCHAR(20) CHECK (Sensor_ID IN ('Entry', 'Menu_Board', 'Order_Point', 'Window', 'Pickup', 'Exit')),
    Arrival_Time TIMESTAMP NOT NULL,
    Departure_Time TIMESTAMP,
    Duration_Seconds INTEGER,
    Car_Count_Hour INTEGER,
    Business_Date DATE
);

-- =============================================================================
-- WORKFORCE TABLES (Harri Ecosystem)
-- =============================================================================

-- 11. Employee_Master_Profile - Staff records
CREATE TABLE IF NOT EXISTS Employee_Master_Profile (
    Employee_ID INTEGER PRIMARY KEY,
    Store_ID INTEGER NOT NULL REFERENCES Organization_Stores(Store_ID),
    Harri_UID VARCHAR(36),
    First_Name VARCHAR(50) NOT NULL,
    Last_Name VARCHAR(50) NOT NULL,
    Role_Code VARCHAR(20) REFERENCES Job_Roles(Role_Code),
    Hire_Date DATE NOT NULL,
    Date_of_Birth DATE,
    Is_Minor BOOLEAN DEFAULT false,
    Hourly_Wage DECIMAL(5,2),
    Email VARCHAR(100),
    Phone VARCHAR(20),
    Food_Handler_Exp DATE,
    Status VARCHAR(20) CHECK (Status IN ('Active', 'Terminated', 'Leave', 'Training')) DEFAULT 'Active'
);

-- 12. Labor_Schedules_Published - Planned shifts
CREATE TABLE IF NOT EXISTS Labor_Schedules_Published (
    Schedule_UUID VARCHAR(36) PRIMARY KEY,
    Store_ID INTEGER NOT NULL REFERENCES Organization_Stores(Store_ID),
    Employee_ID INTEGER NOT NULL REFERENCES Employee_Master_Profile(Employee_ID),
    Shift_Date DATE NOT NULL,
    Shift_Start TIMESTAMP NOT NULL,
    Shift_End TIMESTAMP NOT NULL,
    Scheduled_Hours DECIMAL(4,2),
    Job_Role VARCHAR(20),
    Is_Posted BOOLEAN DEFAULT true,
    Forecast_Sales DECIMAL(10,2),
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. Time_Attendance_Actuals - Actual punches
CREATE TABLE IF NOT EXISTS Time_Attendance_Actuals (
    Punch_UUID VARCHAR(36) PRIMARY KEY,
    Store_ID INTEGER NOT NULL REFERENCES Organization_Stores(Store_ID),
    Employee_ID INTEGER NOT NULL REFERENCES Employee_Master_Profile(Employee_ID),
    Schedule_UUID VARCHAR(36) REFERENCES Labor_Schedules_Published(Schedule_UUID),
    Shift_Date DATE NOT NULL,
    Clock_In_Time TIMESTAMP,
    Clock_Out_Time TIMESTAMP,
    Break_Start TIMESTAMP,
    Break_End TIMESTAMP,
    Break_Duration_Minutes INTEGER,
    Actual_Hours DECIMAL(4,2),
    Validation_Method VARCHAR(20) CHECK (Validation_Method IN ('Biometric', 'Pin', 'Manager_Override')),
    Is_Late BOOLEAN DEFAULT false,
    Late_Minutes INTEGER DEFAULT 0,
    Is_No_Show BOOLEAN DEFAULT false
);

-- 14. Labor_Compliance_Violations - Violation log
CREATE TABLE IF NOT EXISTS Labor_Compliance_Violations (
    Violation_UUID VARCHAR(36) PRIMARY KEY,
    Store_ID INTEGER NOT NULL REFERENCES Organization_Stores(Store_ID),
    Employee_ID INTEGER NOT NULL REFERENCES Employee_Master_Profile(Employee_ID),
    Punch_UUID VARCHAR(36) REFERENCES Time_Attendance_Actuals(Punch_UUID),
    Violation_Date DATE NOT NULL,
    Violation_Type VARCHAR(30) CHECK (Violation_Type IN ('Minor_Overtime', 'Minor_Late_Hours', 'Missed_Break', 'Short_Turnaround', 'Seventh_Day_Overtime', 'Overtime_Without_Approval')),
    Description VARCHAR(255),
    Penalty_Cost DECIMAL(8,2) DEFAULT 0,
    Manager_Ack BOOLEAN DEFAULT false,
    Resolved BOOLEAN DEFAULT false
);

-- =============================================================================
-- INVENTORY TABLES
-- =============================================================================

-- 15. Inventory_Item_Master - Raw materials catalog
CREATE TABLE IF NOT EXISTS Inventory_Item_Master (
    Inventory_ID INTEGER PRIMARY KEY,
    Description VARCHAR(100) NOT NULL,
    Category VARCHAR(50) CHECK (Category IN ('Syrup', 'Puree', 'Dairy', 'Base_Carbonated', 'Energy', 'Paper_Goods', 'Food_Prep', 'Cleaning', 'Ice')),
    Vendor_ID INTEGER REFERENCES Vendors(Vendor_ID),
    Count_UOM VARCHAR(20),  -- Unit of Measure for counting (Bottle, Case, Bag)
    Recipe_UOM VARCHAR(20),  -- Unit of Measure for recipes (oz, pump, ml)
    Conversion_Factor DECIMAL(8,4),  -- Count_UOM to Recipe_UOM
    Unit_Cost DECIMAL(8,4),
    Par_Level DECIMAL(10,2),
    Reorder_Point DECIMAL(10,2),
    Is_Active BOOLEAN DEFAULT true
);

-- 16. Recipe_BOM_Mapping - Product-to-ingredient mapping
CREATE TABLE IF NOT EXISTS Recipe_BOM_Mapping (
    Recipe_ID INTEGER PRIMARY KEY,
    Sales_Item_SKU VARCHAR(20) NOT NULL REFERENCES Product_Catalog(Item_SKU),
    Inventory_ID INTEGER NOT NULL REFERENCES Inventory_Item_Master(Inventory_ID),
    Quantity_Required DECIMAL(8,4) NOT NULL,
    Recipe_UOM VARCHAR(20),
    Yield_Loss_Pct DECIMAL(5,4) DEFAULT 0,
    Is_Optional BOOLEAN DEFAULT false
);

-- 17. Inventory_Transactions_Ledger - Stock movements
CREATE TABLE IF NOT EXISTS Inventory_Transactions_Ledger (
    Trans_UUID VARCHAR(36) PRIMARY KEY,
    Store_ID INTEGER NOT NULL REFERENCES Organization_Stores(Store_ID),
    Inventory_ID INTEGER NOT NULL REFERENCES Inventory_Item_Master(Inventory_ID),
    Transaction_Date DATE NOT NULL,
    Transaction_Time TIMESTAMP NOT NULL,
    Transaction_Type VARCHAR(30) CHECK (Transaction_Type IN ('Delivery_Received', 'Sales_Usage', 'Waste_Log', 'Transfer_Out', 'Transfer_In', 'Audit_Adjustment', 'Theft_Suspected')),
    Quantity_Change DECIMAL(10,4),  -- Positive (in) or Negative (out)
    Running_Balance DECIMAL(10,4),
    Cost_Value DECIMAL(10,4),
    Reason_Code VARCHAR(50),
    Reference_ID VARCHAR(36),  -- Links to Transaction_UUID for sales
    Employee_ID INTEGER REFERENCES Employee_Master_Profile(Employee_ID)
);

-- =============================================================================
-- ADDITIONAL TABLES
-- =============================================================================

-- 18. Daily_Cash_Reconciliation - End-of-day cash counts
CREATE TABLE IF NOT EXISTS Daily_Cash_Reconciliation (
    Reconciliation_UUID VARCHAR(36) PRIMARY KEY,
    Store_ID INTEGER NOT NULL REFERENCES Organization_Stores(Store_ID),
    Business_Date DATE NOT NULL,
    Shift VARCHAR(20) CHECK (Shift IN ('Opening', 'Mid', 'Closing')),
    Expected_Cash DECIMAL(10,2),
    Actual_Cash DECIMAL(10,2),
    Variance DECIMAL(10,2),
    Variance_Pct DECIMAL(5,4),
    Counted_By_Employee_ID INTEGER REFERENCES Employee_Master_Profile(Employee_ID),
    Verified_By_Employee_ID INTEGER REFERENCES Employee_Master_Profile(Employee_ID),
    Count_Timestamp TIMESTAMP,
    Notes VARCHAR(255)
);

-- 19. Discounts_Promotions - Active promos/coupons
CREATE TABLE IF NOT EXISTS Discounts_Promotions (
    Promo_ID INTEGER PRIMARY KEY,
    Promo_Code VARCHAR(20) UNIQUE,
    Promo_Name VARCHAR(100),
    Promo_Type VARCHAR(20) CHECK (Promo_Type IN ('Percent_Off', 'Dollar_Off', 'BOGO', 'Free_Item', 'Happy_Hour')),
    Discount_Value DECIMAL(5,2),
    Min_Purchase DECIMAL(6,2) DEFAULT 0,
    Applicable_Items VARCHAR(255),  -- SKU list or 'ALL'
    Start_Date DATE,
    End_Date DATE,
    Is_Active BOOLEAN DEFAULT true,
    Usage_Count INTEGER DEFAULT 0
);

-- 20. Equipment_Status - Ice machine, soda fountains, etc.
CREATE TABLE IF NOT EXISTS Equipment_Status (
    Status_UUID VARCHAR(36) PRIMARY KEY,
    Store_ID INTEGER NOT NULL REFERENCES Organization_Stores(Store_ID),
    Equipment_ID VARCHAR(20),
    Equipment_Type VARCHAR(50) CHECK (Equipment_Type IN ('Ice_Machine', 'Soda_Fountain', 'Syrup_Pump', 'Refrigerator', 'Freezer', 'POS_Terminal', 'Credit_Card_Reader', 'Drive_Thru_Speaker')),
    Equipment_Name VARCHAR(100),
    Status VARCHAR(20) CHECK (Status IN ('Operational', 'Degraded', 'Down', 'Maintenance')),
    Status_Change_Time TIMESTAMP NOT NULL,
    Expected_Resolution TIMESTAMP,
    Impact_Level VARCHAR(20) CHECK (Impact_Level IN ('None', 'Low', 'Medium', 'High', 'Critical')),
    Notes VARCHAR(255),
    Reported_By_Employee_ID INTEGER REFERENCES Employee_Master_Profile(Employee_ID)
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_transactions_store_date ON Sales_Transactions_Header(Store_ID, Business_Date);
CREATE INDEX IF NOT EXISTS idx_transactions_employee ON Sales_Transactions_Header(Employee_ID);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON Sales_Transactions_Header(Open_Timestamp);
CREATE INDEX IF NOT EXISTS idx_line_items_transaction ON Sales_Order_Line_Items(Transaction_UUID);
CREATE INDEX IF NOT EXISTS idx_line_items_sku ON Sales_Order_Line_Items(Item_SKU);
CREATE INDEX IF NOT EXISTS idx_payments_transaction ON Sales_Payments(Transaction_UUID);
CREATE INDEX IF NOT EXISTS idx_loop_metrics_store_date ON Drive_Thru_Loop_Metrics(Store_ID, Business_Date);
CREATE INDEX IF NOT EXISTS idx_employees_store ON Employee_Master_Profile(Store_ID);
CREATE INDEX IF NOT EXISTS idx_schedules_employee_date ON Labor_Schedules_Published(Employee_ID, Shift_Date);
CREATE INDEX IF NOT EXISTS idx_attendance_employee_date ON Time_Attendance_Actuals(Employee_ID, Shift_Date);
CREATE INDEX IF NOT EXISTS idx_inventory_ledger_store_date ON Inventory_Transactions_Ledger(Store_ID, Transaction_Date);
CREATE INDEX IF NOT EXISTS idx_inventory_ledger_item ON Inventory_Transactions_Ledger(Inventory_ID);
