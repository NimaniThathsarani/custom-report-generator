Custom Report Generator – Requirements & Report Design
1. Project Overview
Project Name
Custom Report Generator
Purpose
The Custom Report Generator is a web-based reporting system that allows stakeholders to generate reports on demand without requiring technical assistance. Users can select a report type, apply filters, and instantly generate reports in Excel or PDF format.
The system aims to reduce manual reporting effort, improve business decision-making, and provide quick access to important business information.
Objectives
•	Automate report generation.
•	Reduce dependency on technical teams.
•	Support Excel and PDF exports.
•	Enable report scheduling.
•	Improve access to business insights.
2. Report Type 1 – Sales Report
Purpose
The Sales Report provides insights into company sales performance, revenue generation, and regional sales distribution.
Data Fields
Field Name	Description
Sale ID	Unique transaction identifier
Product Name	Name of sold product
Category	Product category
Sale Date	Date of sale
Quantity Sold	Number of units sold
Unit Price	Price per unit
Total Amount	Total sale value
Region	Sales region

Filters
Users should be able to filter the report using:
•	Start Date
•	End Date
•	Product Category
•	Region
Example Usage
A Sales Manager wants to know:
"How much revenue was generated from Electronics products in the Western Province during June 2026?"
The manager selects:
•	Start Date: 2026-06-01
•	End Date: 2026-06-30
•	Category: Electronics
•	Region: Western Province
The system generates a customized report.
Expected Output
•	Total Revenue
•	Total Orders
•	Product-wise Sales Breakdown
•	Region-wise Sales Summary

3. Report Type 2 – User Activity Report
Purpose
The User Activity Report helps monitor user engagement and platform usage.
Data Fields
Field Name	Description
User ID	Unique user identifier
User Name	User name
Login Date	Date of login
Login Time	Time of login
Activity Type	Action performed
Session Duration	Time spent in system
Filters
Users should be able to filter the report using:
•	Start Date
•	End Date
•	User Name
•	Activity Type
Example Usage
A System Administrator wants to identify:
"Which users accessed the system most frequently during the last month?"
The administrator selects:
•	Date Range
•	User Name (optional)
•	Activity Type
The system generates an activity summary.
Expected Output
•	Total Active Users
•	Login Frequency
•	Activity Distribution
•	User Session Statistics
4. Report Type 3 – Inventory Report
Purpose
The Inventory Report provides visibility into stock levels and product availability.
Data Fields
Field Name	Description
Product ID	Product identifier
Product Name	Product name
Category	Product category
Current Stock	Available quantity
Reorder Level	Minimum stock threshold
Warehouse Location	Storage location
Filters
Users should be able to filter the report using:
•	Product Category
•	Warehouse Location
Example Usage
An Inventory Manager wants to identify:
"Which products are below their reorder level in the Colombo warehouse?"
The manager selects:
•	Warehouse Location
•	Product Category
The system generates a stock status report.
Expected Output
•	Current Inventory Levels
•	Low Stock Products
•	Reorder Alerts
•	Inventory by Category
5. Export Requirements
All reports must support:
Excel Export (.xlsx)
Generated using OpenPyXL.
Purpose:
•	Further analysis
•	Spreadsheet editing
•	Data sharing
PDF Export (.pdf)
Generated using Report Lab.
Purpose:
•	Printing
•	Presentations
•	Management reporting
6. Scheduling Requirements
The system should allow recurring report generation.
Scheduling Options
•	Daily
•	Weekly
•	Monthly
Scheduling Parameters
•	Report Type
•	Date and Time
•	Export Format
Example
A manager can schedule:
Sales Report every Monday at 8:00 AM
The system automatically generates the report according to the schedule.
7. Summary
The Custom Report Generator will initially support three report types:
1.	Sales Report
2.	User Activity Report
3.	Inventory Report
Each report includes clearly defined fields and filters that allow users to generate customized reports based on business requirements.
These requirements provide sufficient detail for the backend development team to:
•	Design database tables
•	Create API endpoints
•	Implement filtering functionality
•	Generate Excel and PDF reports
•	Configure automated scheduling
This document serves as the foundation for the development and implementation of the Custom Report Generator system.
Report Type	Fields	Filters
Sales Report	Sale ID, Product Name, Category, Sale Date, Quantity, Amount, Region	Date Range, Category, Region
User Activity Report	User ID, User Name, Login Date, Activity Type, Session Duration	Date Range, User Name, Activity Type
Inventory Report	Product ID, Product Name, Category, Stock, Reorder Level, Warehouse	Category, Warehouse

