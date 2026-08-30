# Credlanche
Automation Test

Key Test Scenarios Covered
- Functional Ingestion (202 Accepted): Validates payload acceptance, queue assignment, and unique job_id generation.
- Contract & Schema Validation (400 Bad Request): Asserts field presence (to), RFC 5322 recipient formatting, and raw JSON syntax integrity.
- Queue Saturated Degradation (503 Service Unavailable): Simulates background worker buffer overflow and asserts presence of the Retry-After response header.
- Client-Side Resilience & Retry Simulation: Verifies exponential backoff logic across transient 503 Service Unavailable states.
- Security Fuzzing (CWE-93 / MITRE T1566.002): Tests parameter resilience against CRLF (\r\n / %0D%0A) SMTP header injection and script tag sanitization.

Setup & Installation
Prerequisites
-Python 3.9+
- Grafana k6 (Optional, for running load test scripts)

Environment Setup
1. Clone the repository:

git clone https://github.com/your-username/email-microservice-qa-suite.git
cd email-microservice-qa-suite

2. Create and activate a virtual environment:
python3 -m venv venv
source venv/bin/activate
# On Windows: venv\Scripts\activate

3. Install dependencies:
4. pip install -r requirements.txt

The requirements.txt file usually only has:
pytest>=7.4.0
requests>=2.31.0

Execute Test Suites:
Execute the complete Python test suite with verbose output:
pytest test_email_microservice.py -v

However to run a specific test scenario (e.g., Security CRLF Injection):
pytest test_email_microservice.py -k "test_security_crlf_injection_prevention" -v

Run Performance & Concurrency Load Tests (k6):
k6 run k6_load_test.js

OR

download the test email microservice file and run Automated Functional & Security Tests (pytest) using pytest test_email_microservice.py -v


Author
Hope David Michael

Cybersecurity & Quality Assurance Engineer

Save the test_email_microservice.py file and run it using pytest test_email_microservice.py -v
