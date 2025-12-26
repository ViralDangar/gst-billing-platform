# GST Billing Platform - API Documentation

Complete API reference for the GST Billing Platform with request/response examples.

---

## Table of Contents

1. [Identity Service](#identity-service)
   - [Company Management](#company-management)
   - [GSTIN Management](#gstin-management)
2. [Master Data Service](#master-data-service)
   - [Product Management](#product-management)
   - [Customer Management](#customer-management)
3. [Billing Service](#billing-service)
   - [Invoice Management](#invoice-management)
4. [Tax Engine Service](#tax-engine-service)

---

## Base URL

```
http://localhost:8000
```

---

## 1. Identity Service

### Company Management

#### Create Company
**POST** `/identity/company`

Creates a new company. Only one company is allowed per system.

**Request Body:**
```json
{
  "name": "ABC Enterprises Pvt Ltd",
  "address": "123 Business Street, Mumbai, Maharashtra - 400001",
  "logo_url": "https://example.com/logo.png",
  "default_bank_details": {
    "bank_name": "HDFC Bank",
    "account_number": "1234567890",
    "ifsc_code": "HDFC0001234",
    "branch": "Mumbai Main"
  }
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "ABC Enterprises Pvt Ltd",
  "address": "123 Business Street, Mumbai, Maharashtra - 400001",
  "logo_url": "https://example.com/logo.png",
  "default_bank_details": {
    "bank_name": "HDFC Bank",
    "account_number": "1234567890",
    "ifsc_code": "HDFC0001234",
    "branch": "Mumbai Main"
  },
  "created_at": "2025-12-26T10:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Company already exists
- `500 Internal Server Error` - Database error

---

#### Get Company
**GET** `/identity/company`

Retrieves the company details.

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "ABC Enterprises Pvt Ltd",
  "address": "123 Business Street, Mumbai, Maharashtra - 400001",
  "logo_url": "https://example.com/logo.png",
  "default_bank_details": {
    "bank_name": "HDFC Bank",
    "account_number": "1234567890",
    "ifsc_code": "HDFC0001234",
    "branch": "Mumbai Main"
  },
  "created_at": "2025-12-26T10:30:00Z"
}
```

**Error Responses:**
- `404 Not Found` - Company not found
- `500 Internal Server Error` - Database error

---

#### Update Company
**PUT** `/identity/company`

Updates the existing company. Only provided fields will be updated.

**Request Body:**
```json
{
  "name": "ABC Enterprises Private Limited",
  "logo_url": "https://example.com/new-logo.png"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "ABC Enterprises Private Limited",
  "address": "123 Business Street, Mumbai, Maharashtra - 400001",
  "logo_url": "https://example.com/new-logo.png",
  "default_bank_details": {
    "bank_name": "HDFC Bank",
    "account_number": "1234567890",
    "ifsc_code": "HDFC0001234",
    "branch": "Mumbai Main"
  },
  "created_at": "2025-12-26T10:30:00Z"
}
```

**Error Responses:**
- `404 Not Found` - Company not found
- `400 Bad Request` - Validation error
- `500 Internal Server Error` - Database error

---

### GSTIN Management

#### Add GSTIN
**POST** `/identity/company/{company_id}/gstins`

Adds a new GSTIN for a company. A company can have multiple GSTINs for different states.

**Path Parameters:**
- `company_id` (UUID) - Company ID

**Request Body:**
```json
{
  "gst_number": "27AABCU9603R1ZM",
  "state_code": "27"
}
```

**Response (201 Created):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "company_id": "550e8400-e29b-41d4-a716-446655440000",
  "gst_number": "27AABCU9603R1ZM",
  "state_code": "27",
  "created_at": "2025-12-26T10:35:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - GSTIN already exists
- `500 Internal Server Error` - Database error

---

#### List GSTINs (Paginated)
**GET** `/identity/company/{company_id}/gstins?page=1&page_size=10`

Lists all GSTINs for a company with pagination.

**Path Parameters:**
- `company_id` (UUID) - Company ID

**Query Parameters:**
- `page` (integer, default: 1) - Page number
- `page_size` (integer, default: 10, max: 100) - Items per page

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "company_id": "550e8400-e29b-41d4-a716-446655440000",
      "gst_number": "27AABCU9603R1ZM",
      "state_code": "27",
      "created_at": "2025-12-26T10:35:00Z"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440002",
      "company_id": "550e8400-e29b-41d4-a716-446655440000",
      "gst_number": "29AABCU9603R1ZN",
      "state_code": "29",
      "created_at": "2025-12-26T11:00:00Z"
    }
  ],
  "total": 2,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

**Error Responses:**
- `500 Internal Server Error` - Database error

---

## 2. Master Data Service

### Product Management

#### Create Product
**POST** `/masters/products`

Creates a new product in the system.

**Request Body:**
```json
{
  "name": "Laptop - Dell Inspiron 15",
  "hsn_sac": "8471",
  "gst_rate": 18.00,
  "unit": "PCS",
  "base_price": 45000.00
}
```

**Response (201 Created):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440003",
  "name": "Laptop - Dell Inspiron 15",
  "hsn_sac": "8471",
  "gst_rate": 18.00,
  "unit": "PCS",
  "base_price": 45000.00,
  "is_active": true,
  "created_at": "2025-12-26T11:15:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Validation error or duplicate product
- `500 Internal Server Error` - Database error

---

#### List Products (Paginated)
**GET** `/masters/products?page=1&page_size=10`

Lists all active products with pagination.

**Query Parameters:**
- `page` (integer, default: 1) - Page number
- `page_size` (integer, default: 10, max: 100) - Items per page

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440003",
      "name": "Laptop - Dell Inspiron 15",
      "hsn_sac": "8471",
      "gst_rate": 18.00,
      "unit": "PCS",
      "base_price": 45000.00,
      "is_active": true,
      "created_at": "2025-12-26T11:15:00Z"
    },
    {
      "id": "770e8400-e29b-41d4-a716-446655440004",
      "name": "Mouse - Logitech MX Master 3",
      "hsn_sac": "8471",
      "gst_rate": 18.00,
      "unit": "PCS",
      "base_price": 7500.00,
      "is_active": true,
      "created_at": "2025-12-26T11:20:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 10,
  "total_pages": 3
}
```

**Error Responses:**
- `500 Internal Server Error` - Database error

---

#### Get Product
**GET** `/masters/products/{product_id}`

Retrieves a single product by ID.

**Path Parameters:**
- `product_id` (UUID) - Product ID

**Response (200 OK):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440003",
  "name": "Laptop - Dell Inspiron 15",
  "hsn_sac": "8471",
  "gst_rate": 18.00,
  "unit": "PCS",
  "base_price": 45000.00,
  "is_active": true,
  "created_at": "2025-12-26T11:15:00Z"
}
```

**Error Responses:**
- `404 Not Found` - Product not found
- `500 Internal Server Error` - Database error

---

#### Update Product
**PUT** `/masters/products/{product_id}`

Updates an existing product. Only provided fields will be updated.

**Path Parameters:**
- `product_id` (UUID) - Product ID

**Request Body:**
```json
{
  "base_price": 42000.00,
  "gst_rate": 18.00
}
```

**Response (200 OK):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440003",
  "name": "Laptop - Dell Inspiron 15",
  "hsn_sac": "8471",
  "gst_rate": 18.00,
  "unit": "PCS",
  "base_price": 42000.00,
  "is_active": true,
  "created_at": "2025-12-26T11:15:00Z"
}
```

**Error Responses:**
- `404 Not Found` - Product not found
- `400 Bad Request` - Validation error
- `500 Internal Server Error` - Database error

---

### Customer Management

#### Create Customer
**POST** `/masters/customer`

Creates a new customer in the system.

**Request Body:**
```json
{
  "name": "XYZ Corporation",
  "gstin": "29AABCX1234F1Z5",
  "state": "Karnataka",
  "address": "456 Tech Park, Bangalore, Karnataka - 560001",
  "is_b2b": true
}
```

**Response (201 Created):**
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440005",
  "name": "XYZ Corporation",
  "gstin": "29AABCX1234F1Z5",
  "state": "Karnataka",
  "address": "456 Tech Park, Bangalore, Karnataka - 560001",
  "is_b2b": true,
  "is_active": true,
  "created_at": "2025-12-26T12:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request` - Validation error or duplicate GSTIN
- `500 Internal Server Error` - Database error

---

#### List Customers (Paginated)
**GET** `/masters/customer?page=1&page_size=10`

Lists all active customers with pagination.

**Query Parameters:**
- `page` (integer, default: 1) - Page number
- `page_size` (integer, default: 10, max: 100) - Items per page

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440005",
      "name": "XYZ Corporation",
      "gstin": "29AABCX1234F1Z5",
      "state": "Karnataka",
      "address": "456 Tech Park, Bangalore, Karnataka - 560001",
      "is_b2b": true,
      "is_active": true,
      "created_at": "2025-12-26T12:00:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 10,
  "total_pages": 2
}
```

**Error Responses:**
- `500 Internal Server Error` - Database error

---

#### Get Customer
**GET** `/masters/customer/{customer_id}`

Retrieves a single customer by ID.

**Path Parameters:**
- `customer_id` (UUID) - Customer ID

**Response (200 OK):**
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440005",
  "name": "XYZ Corporation",
  "gstin": "29AABCX1234F1Z5",
  "state": "Karnataka",
  "address": "456 Tech Park, Bangalore, Karnataka - 560001",
  "is_b2b": true,
  "is_active": true,
  "created_at": "2025-12-26T12:00:00Z"
}
```

**Error Responses:**
- `404 Not Found` - Customer not found
- `500 Internal Server Error` - Database error

---

#### Update Customer
**PUT** `/masters/customer/{customer_id}`

Updates an existing customer. Only provided fields will be updated.

**Path Parameters:**
- `customer_id` (UUID) - Customer ID

**Request Body:**
```json
{
  "address": "789 New Tech Park, Bangalore, Karnataka - 560002",
  "is_active": true
}
```

**Response (200 OK):**
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440005",
  "name": "XYZ Corporation",
  "gstin": "29AABCX1234F1Z5",
  "state": "Karnataka",
  "address": "789 New Tech Park, Bangalore, Karnataka - 560002",
  "is_b2b": true,
  "is_active": true,
  "created_at": "2025-12-26T12:00:00Z"
}
```

**Error Responses:**
- `404 Not Found` - Customer not found
- `400 Bad Request` - Validation error
- `500 Internal Server Error` - Database error

---

## 3. Billing Service

### Invoice Management

#### Create Invoice
**POST** `/billing/invoices/`

Creates a new invoice in DRAFT status. If `gstin_id` is not provided, it automatically assigns the first available GSTIN.

**Request Body:**
```json
{
  "invoice_date": "2025-12-26",
  "customer_id": "880e8400-e29b-41d4-a716-446655440005",
  "gstin_id": "660e8400-e29b-41d4-a716-446655440001"
}
```

**Note:** `gstin_id` is optional. If omitted, the system auto-assigns the first GSTIN.

**Response (201 Created):**
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440006",
  "invoice_date": "2025-12-26",
  "gstin_id": "660e8400-e29b-41d4-a716-446655440001",
  "customer_id": "880e8400-e29b-41d4-a716-446655440005",
  "status": "DRAFT",
  "items": []
}
```

**Error Responses:**
- `400 Bad Request` - Validation error or no GSTIN available
- `500 Internal Server Error` - Database error

---

#### Add Invoice Item
**POST** `/billing/invoices/{invoice_id}/items`

Adds an item to an existing DRAFT invoice. Automatically calculates taxable value.

**Path Parameters:**
- `invoice_id` (UUID) - Invoice ID

**Request Body:**
```json
{
  "product_id": "770e8400-e29b-41d4-a716-446655440003",
  "quantity": 2,
  "rate": 42000.00
}
```

**Response (200 OK):**
```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440007",
  "invoice_id": "990e8400-e29b-41d4-a716-446655440006",
  "product_id": "770e8400-e29b-41d4-a716-446655440003",
  "quantity": 2.00,
  "rate": 42000.00,
  "taxable_value": 84000.00
}
```

**Error Responses:**
- `404 Not Found` - Invoice not found
- `400 Bad Request` - Invoice not in DRAFT status or invalid product_id
- `500 Internal Server Error` - Database error

---

#### Get Invoice
**GET** `/billing/invoices/{invoice_id}`

Retrieves a single invoice with all its items.

**Path Parameters:**
- `invoice_id` (UUID) - Invoice ID

**Response (200 OK):**
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440006",
  "invoice_date": "2025-12-26",
  "gstin_id": "660e8400-e29b-41d4-a716-446655440001",
  "customer_id": "880e8400-e29b-41d4-a716-446655440005",
  "status": "DRAFT",
  "items": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440007",
      "product_id": "770e8400-e29b-41d4-a716-446655440003",
      "quantity": 2.00,
      "rate": 42000.00,
      "taxable_value": 84000.00
    }
  ]
}
```

**Error Responses:**
- `404 Not Found` - Invoice not found
- `500 Internal Server Error` - Database error

---

#### List Invoices (Paginated)
**GET** `/billing/invoices/?page=1&page_size=10`

Lists all invoices with pagination.

**Query Parameters:**
- `page` (integer, default: 1) - Page number
- `page_size` (integer, default: 10, max: 100) - Items per page

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440006",
      "invoice_number": null,
      "invoice_date": "2025-12-26",
      "gstin_id": "660e8400-e29b-41d4-a716-446655440001",
      "customer_id": "880e8400-e29b-41d4-a716-446655440005",
      "status": "DRAFT",
      "taxable_total": null,
      "tax_total": null,
      "round_off": null,
      "grand_total": null,
      "created_at": "2025-12-26T13:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 10,
  "total_pages": 5
}
```

**Error Responses:**
- `500 Internal Server Error` - Database error

---

#### Finalize Invoice
**POST** `/billing/invoices/{invoice_id}/finalize`

Finalizes an invoice by changing status from DRAFT to FINALIZED and generating a unique invoice number.

**Path Parameters:**
- `invoice_id` (UUID) - Invoice ID

**Response (200 OK):**
```json
{
  "invoice_id": "990e8400-e29b-41d4-a716-446655440006",
  "invoice_number": "INV/2025-26/000001",
  "status": "FINALIZED"
}
```

**Error Responses:**
- `400 Bad Request` - Invoice cannot be finalized (validation error)
- `500 Internal Server Error` - Database error

---

## 4. Tax Engine Service

#### Calculate GST
**POST** `/tax/calculate`

Calculates GST for a DRAFT invoice. Determines whether to apply CGST+SGST (intra-state) or IGST (inter-state) based on seller and customer locations.

**Request Body:**
```json
{
  "invoice_id": "990e8400-e29b-41d4-a716-446655440006"
}
```

**Response (200 OK):**
```json
{
  "invoice_id": "990e8400-e29b-41d4-a716-446655440006",
  "taxable_total": 84000.00,
  "tax_total": 15120.00,
  "grand_total": 99120.00
}
```

**Tax Calculation Logic:**
- **Intra-state (same state):** CGST (9%) + SGST (9%) = 18%
- **Inter-state (different states):** IGST (18%)

**Error Responses:**
- `400 Bad Request` - Invoice not found, not in DRAFT, no items, missing GSTIN, etc.
- `500 Internal Server Error` - Database error

---

## Health Check Endpoints

#### Billing Service Health
**GET** `/billing/invoices/health`

**Response (200 OK):**
```json
{
  "service": "billing",
  "status": "ok"
}
```

---

#### Master Data Service Health
**GET** `/masters/products/health`

**Response (200 OK):**
```json
{
  "service": "master-data",
  "status": "ok"
}
```

---

#### Identity Service Health
**GET** `/identity/health`

**Response (200 OK):**
```json
{
  "service": "identity",
  "status": "ok"
}
```

---

## Common Error Response Format

All endpoints follow a consistent error response format:

**Error Response (4xx/5xx):**
```json
{
  "detail": "Error message describing what went wrong"
}
```

**HTTP Status Codes Used:**
- `200 OK` - Successful GET/PUT request
- `201 Created` - Successful POST request (resource created)
- `400 Bad Request` - Validation error or business logic error
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Database error or unexpected server error

---

## Pagination Format

All list endpoints support pagination with the following format:

**Query Parameters:**
- `page` (integer, default: 1, min: 1) - Page number
- `page_size` (integer, default: 10, min: 1, max: 100) - Items per page

**Response Format:**
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "total_pages": 10
}
```

---

## Complete Workflow Example

### 1. Setup Company and GSTIN

```bash
# Create Company
POST /identity/company
{
  "name": "ABC Enterprises Pvt Ltd",
  "address": "Mumbai, Maharashtra",
  "logo_url": "https://example.com/logo.png",
  "default_bank_details": {...}
}

# Add GSTIN
POST /identity/company/{company_id}/gstins
{
  "gst_number": "27AABCU9603R1ZM",
  "state_code": "27"
}
```

### 2. Create Master Data

```bash
# Create Product
POST /masters/products
{
  "name": "Laptop",
  "hsn_sac": "8471",
  "gst_rate": 18.00,
  "unit": "PCS",
  "base_price": 45000.00
}

# Create Customer
POST /masters/customer
{
  "name": "XYZ Corp",
  "gstin": "29AABCX1234F1Z5",
  "state": "Karnataka",
  "address": "Bangalore",
  "is_b2b": true
}
```

### 3. Create Invoice and Add Items

```bash
# Create Invoice
POST /billing/invoices/
{
  "invoice_date": "2025-12-26",
  "customer_id": "{customer_id}"
}
# Note: gstin_id is auto-assigned

# Add Items
POST /billing/invoices/{invoice_id}/items
{
  "product_id": "{product_id}",
  "quantity": 2,
  "rate": 42000.00
}
```

### 4. Calculate Tax

```bash
# Calculate GST
POST /tax/calculate
{
  "invoice_id": "{invoice_id}"
}
```

### 5. Finalize Invoice

```bash
# Finalize
POST /billing/invoices/{invoice_id}/finalize
```

---

## Notes

- All UUIDs are in standard UUID v4 format
- All dates are in ISO 8601 format (YYYY-MM-DD)
- All timestamps are in ISO 8601 format with timezone (YYYY-MM-DDTHH:MM:SSZ)
- Decimal values support up to 2 decimal places for currency
- GST rates are stored as percentages (e.g., 18.00 for 18%)

---

**Generated:** 2025-12-26
**Version:** 1.0
**Platform:** GST Billing Platform
