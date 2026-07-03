tive analysis of ~175 models across Claude, OpenAI, Gemini, and xAI, evaluating them from platform capability to agent-level governance perspectives.
I will talk with Kannann, and share the outcome of the work. 
Thanks again for the approval and guidance.
With regards,

Ram
From: Anupama Gangadhar <anupama.gangadhar@mastechdigital.com>Sent: Thursday, May 14, 2026 3:56 PMTo: Ramamurthy Valavandan <ramamurthy.valavandan@mastechdigital.com>; Kannann Velmurugiah <kannann.velmurugiah@mastechdigital.com>Cc: Arun Kumar G <arunkumar.g@mastechdigital.com>; Siddharth Jothimani <siddharth.j@mastechdigital.com>Subject: RE: Approval Request: Snowflake DEV Access (Public Schema Only)
 
Never seen such a murder of my name 😃
 
Approved with * condition – you have to come back and share the knowledge in larger forum with Snowflake studio folks.
 
+ Kannan – He might have already done some of these comparisons so sync up before you start.
 
@Kannann Velmurugiah
 
Please see what Ram requires. Preferably a dedicated schema/role/wh to work with.
 
Thank you,
Regards,
Anupama
 From: Ramamurthy Valavandan <ramamurthy.valavandan@mastechdigital.com>Sent: 14 May 2026 15:11To: Anupama Gangadhar <anupama.gangadhar@mastechdigital.com>Cc: Arun Kumar G <arunkumar.g@mastechdigital.com>; Siddharth Jothimani <siddharth.j@mastechdigital.com>Subject: Approval Request: Snowflake DEV Access (Public Schema Only)
 
Hi Annupana,
I am requesting your approval to raise a Snowflake access ticket with strictly limited scope.
The access is required only for the DEV environment, limited to the default database and PUBLIC schema, and will be used solely for Data Engineering evaluation and schema/data‑model comparison activities. This includes comparison with Codex, Compare Codex, and AIDER for catalog intelligence and data modeling use cases.
The usage is purely for internal POC and evaluation and will comply with all security and governance guidelines.
 
Thanks & regards,
Ramamurthy
You
Sat 5/23/2026 9:19 AM
Hi Anupama, Good morning. Thank you for your previous approval on Snowflake DEV access. I am currently progressing with Phase 10 of the Enterprise Knowledge Fabric (EKF), which involves setting up a federated data pipeline from Snowflake → GCS → BigQuery BigLake
You
Fri 5/15/2026 7:39 AM
Hi Nirmal I have attached the approval in the IT Ticket Thanks Ram
Nirmalraj Velu
Thu 5/14/2026 6:29 PM
Pls attach this approval with IT ticket, will review and proceed on this Thanks, Nirmal.
You
Thu 5/14/2026 4:03 PM
(No message text)
You
Thu 5/14/2026 4:03 PM
Hi Anupama , Apologies for the incorrect name reference earlier. The work I’m carrying out is part of AI Governance initiatives in OSSA, focusing on governance provisions across platform layers and agentic governance. As part of this, I’ve already done a comparative
Anupama Gangadhar
Thu 5/14/2026 3:57 PM
Never seen such a murder of my name 😃 Approved with * condition – you have to come back and share the knowledge in larger forum with Snowflake studio folks. + Kannan – He might have already done some of these comparisons so sync up before you start. @Kannann
You
Thu 5/14/2026 3:10 PM
Hi Annupana, I am requesting your approval to raise a Snowflake access ticket with strictly limited scope. The access is required only for the DEV environment, limited to the default database and PUBLIC schema, and will be used solely for Data Engineering evaluation 



[Attached File: image/jpeg, Size: 228876 bytes]


 gui ete full steps wher eo brinegingin ui


[Attached File: image/jpeg, Size: 356448 bytes]


 The error occurs because the storage integration SF_GCS_INTEGRATION referenced in your stage creation (line 142) doesn't exist in your account, or your role CAPABILITY_ASSESSMENT doesn't have USAGE privileges on it.
Storage integrations are account-level objects that must be created by an ACCOUNTADMIN. Let me check what's available:
List available storage integrations


No storage integrations exist in your account (or are visible to your current role). To fix this, you need an ACCOUNTADMIN to:
Create the storage integration:
sql
USE ROLE ACCOUNTADMIN;

CREATE OR REPLACE STORAGE INTEGRATION sf_gcs_integration
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'GCS'
  ENABLED = TRUE
  STORAGE_ALLOWED_LOCATIONS = ('gcs://ekf-biglake-feed/');
Grant usage to your role:
sql
GRANT USAGE ON INTEGRATION sf_gcs_integration TO ROLE CAPABILITY_ASSESSMENT;
Retrieve the service account (needed to configure GCS bucket access):
sql
DESCRIBE STORAGE INTEGRATION sf_gcs_integration;
The STORAGE_GCP_SERVICE_ACCOUNT value must be granted the Storage Object Admin role on your GCS bucket ekf-biglake-feed.
Your current role CAPABILITY_ASSESSMENT cannot create storage integrations — this requires ACCOUNTADMIN or a role with CREATE INTEGRATION privilege


can we use this with expisting permisons any oyher alertave

I can't execute gcloud CLI commands from this Snowflake Workspace environment — only ls, dbt, and snow commands are available here.
However, you also cannot directly download staged files from a Snowflake internal stage to GCS within Snowflake. Here are your two options:
Option 1: Download via Snowsight UI, then upload locally
In Snowsight sidebar: Data → Databases → CAPABILITY_ASSESSMENT → EKF → Stages → ekf_internal_stage
Navigate to customers/year=2026/month=05/
Click Download on data_0_0_0.snappy.parquet
Then from your local terminal:
bash
gcloud storage cp ~/Downloads/data_0_0_0.snappy.parquet \
  gs://ekf-biglake-feed/unload/customers/year=2026/month=05/data_0_0_0.snappy.parquet
Option 2: Use SnowSQL GET from your local machine
bash
snowsql -a xna38553 -u "RAMAMURTHY.VALAVANDAN@MASTECHDIGITAL.COM" -r CAPABILITY_ASSESSMENT -w CAPABILITY_ASSESSMENT_WH -d CAPABILITY_ASSESSMENT -s EKF -q "GET @ekf_internal_stage/customers/year=2026/month=05/ file:///tmp/ekf_export/"

gcloud storage cp /tmp/ekf_export/data_0_0_0.snappy.parquet \
  gs://ekf-biglake-feed/unload/customers/year=2026/month=05/
Both approaches require running commands from your local machine or Cloud Shell — not from this Snowflake Workspace. # EKF Phase 10 – Snowflake Internal Stage Export
Federated data pipeline using internal stage (no storage integration required).
%%sql -r context_setup
USE ROLE CAPABILITY_ASSESSMENT;
USE WAREHOUSE CAPABILITY_ASSESSMENT_WH;
USE DATABASE CAPABILITY_ASSESSMENT;
USE SCHEMA EKF;
%%sql -r create_table_result
CREATE OR REPLACE TABLE CAPABILITY_ASSESSMENT.EKF.raw_customers (
 customer_id INT,
 first_name VARCHAR(100),
 last_name VARCHAR(100),
 email VARCHAR(255),
 loyalty_segment VARCHAR(50),
 signup_date DATE
);
%%sql -r insert_result
INSERT INTO CAPABILITY_ASSESSMENT.EKF.raw_customers (customer_id, first_name, last_name, email, loyalty_segment, signup_date) VALUES
 (1001, 'John', 'Doe', 'john.doe@retailmail.com', 'Gold', '2025-01-15'),
 (1002, 'Jane', 'Smith', 'jane.smith@retailmail.com', 'Platinum', '2024-11-20'),
 (1003, 'Alex', 'Johnson', 'alex.j@retailmail.com', 'Standard', '2026-02-10'),
 (1004, 'Michael', 'Brown', 'm.brown@retailmail.com', 'Gold', '2025-06-05'),
 (1005, 'Emily', 'Davis', 'emily.d@retailmail.com', 'Standard', '2026-04-18');
-- Skip: CREATE FILE FORMAT requires privilege not granted to this role.
-- File format will be specified inline on the stage instead.
SELECT 'File format will be defined inline on stage' AS status;
CREATE OR REPLACE STAGE CAPABILITY_ASSESSMENT.EKF.ekf_internal_stage
 FILE_FORMAT = (TYPE = 'PARQUET' COMPRESSION = 'SNAPPY');
CREATE OR REPLACE VIEW CAPABILITY_ASSESSMENT.EKF.v_export_customers_secured AS
SELECT 
 customer_id,
 first_name,
 last_name,
 email,
 'Confidential' AS sensitivity_level,
 'customer_domain' AS owner_domain,
 TO_VARCHAR(CURRENT_TIMESTAMP(), 'YYYY-MM-DD HH24:MI:SS') AS export_timestamp
FROM CAPABILITY_ASSESSMENT.EKF.raw_customers;
COPY INTO @CAPABILITY_ASSESSMENT.EKF.ekf_internal_stage/customers/year=2026/month=05/
FROM CAPABILITY_ASSESSMENT.EKF.v_export_customers_secured
OVERWRITE = TRUE
HEADER = TRUE;
%%sql -r list_result
LIST @CAPABILITY_ASSESSMENT.EKF.ekf_internal_stage/customers/year=2026/month=05/;
 LET ME KNWO WHETER LL TE SNOWLFEAKE IS DONE WE OR DO WE N TO ADDMORE ENTIS AN DI WILL RUN TEH STEPS IN 10.100.15.31 IN GCP ?



# 1. Create a local temporary directory for the export mkdir -p /tmp/ekf_export/ # 2. Execute SnowSQL to retrieve the staged Parquet file snowsql -a xna38553 -u "RAMAMURTHY.VALAVANDAN@MASTECHDIGITAL.COM" \ -r CAPABILITY_ASSESSMENT -w CAPABILITY_ASSESSMENT_WH \ -d CAPABILITY_ASSESSMENT -s EKF \ -q "GET @ekf_internal_stage/customers/year=2026/month=05/ file:///tmp/ekf_export/" CAN I CREATEIN 
appadmin@chn-mit-genai-dq1://$ cd
appadmin@chn-mit-genai-dq1:~$ cd projects/Ram_Projects/DiracDelta/ekf/
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ pwd
/home/appadmin/projects/Ram_Projects/DiracDelta/ekf
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$
 


appadmin@chn-mit-genai-dq1://$ cd
appadmin@chn-mit-genai-dq1:~$ cd -
//
appadmin@chn-mit-genai-dq1://$ cd
appadmin@chn-mit-genai-dq1:~$ cd projects/Ram_Projects/DiracDelta/ekf/
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ pwd
/home/appadmin/projects/Ram_Projects/DiracDelta/ekf
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ nano scripts/snowflake_to_gcs.py
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ # 1. Activate the venv
source .venv-vllm/bin/activate

# 2. Install google storage package (if not already installed)
pip install google-cloud-storage --quiet

# 3. Install SnowSQL CLI onto your VM
curl -O https://sfc-repo.snowflakecomputing.com/snowsql/bootstrap/1.2/linux_x86_64/snowsql-1.2.32-linux_x86_64.bash
bash snowsql-1.2.32-linux_x86_64.bash -b ~/bin

# 4. Expose snowsql path
export PATH=$PATH:~/bin
echo 'export PATH=$PATH:~/bin' >> ~/.bashrc

# 5. Make the pipeline script executable and run
chmod +x scripts/snowflake_to_gcs.py
python3 scripts/snowflake_to_gcs.py
 % Total  % Received % Xferd Average Speed  Time  Time   Time Current
                 Dload Upload  Total  Spent  Left Speed
100 48.8M 100 48.8M  0   0 18.1M   0 0:00:02 0:00:02 --:--:-- 18.1M
**********************************************************************
 Installing SnowSQL, Snowflake CLI.
**********************************************************************

Specify the directory in which the SnowSQL components will be installed. [~/bin]
Do you want to add /home/appadmin/bin to PATH in /home/appadmin/.profile? [y/N]
**********************************************************************
 Congratulations! Follow the steps to connect to Snowflake DB.
**********************************************************************

1. Open a new terminal window.
2. Execute the following command to test your connection:
   snowsql -a <account_name> -u <login_name>

   Enter your password when prompted. Enter !quit to quit the connection.

3. Add your connection information to the ~/.snowsql/config file:
   accountname = <account_name>
        username = <login_name>
        password = <password>

4. Execute the following command to connect to Snowflake:

   snowsql

See the Snowflake documentation <https://docs.snowflake.net/manuals/user-guide/snowsql.html> for more information.
Loading environment variables from: /home/appadmin/projects/Ram_Projects/DiracDelta/ekf/.env.local
==================================================
Mastech ADEPT: Snowflake to GCS Export Pipeline
==================================================
Connecting to Snowflake and fetching staged Parquet data...
Password:

 this is my login rijgt what to have the hthi spassword or can we have the logn or api from the snowlfalke to gcp ? how the alos we willbe usinge biglae if you recall

btw, how to ge the snowlfalke password or do we have aotehr way linek service account or adc like in gcp we ne dto aev for thei appin biglakess right

ure 2048-bit private key
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt

# 2. Extract the matching public key
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
writing RSA key
(.venv-vllm) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$

 i wll copyt nas pasge the ras key in sknwofale gibe te seps pr can 


[Attached File: image/jpeg, Size: 287044 bytes]


 what to ask in cordex in snowlfake to tets the fromteh gcp to us eth ebigalake conector now atelae swhete rthis ins ok

how to see theis key PASTE_YOUR_CLEAN_PUBLIC_KEY_STRING_HERE>

Read /Untitled 1.sql (lines 1-3)

Read results
The ALTER USER command requires elevated privileges (ACCOUNTADMIN or SECURITYADMIN) — your current PUBLIC role cannot modify user properties.
You have two options:
Ask your DBA (Yatindra/Kannan) to run this on your behalf as ACCOUNTADMIN:
sql
USE ROLE ACCOUNTADMIN;
ALTER USER "RAMAMURTHY.VALAVANDAN@MASTECHDIGITAL.COM" 
  SET RSA_PUBLIC_KEY='MIIBIjANBgkqhkiG9w0BAQE...';
Try with your CAPABILITY_ASSESSMENT role (unlikely to work for ALTER USER, but worth trying):
sql
USE ROLE CAPABILITY_ASSESSMENT;
ALTER USER "RAMAMURTHY.VALAVANDAN@MASTECHDIGITAL.COM" 
  SET RSA_PUBLIC_KEY='...';
In Snowflake, only roles with the OWNERSHIP privilege on the user object (typically ACCOUNTADMIN or SECURITYADMIN) can alter user properties like RSA_PUBLIC_KEY. This must be done by your admin team.
Open

Untitled 1.sql



if i ne dto do myself cn i do here in snowlfake also ie dto undertsna if we hodt this app i broud hiw cwe do that ex if i ve t gcp whetehr still sme teh ras is hold or yoe ay o ge the 5 iyears

like adbck gclpud anpth can i rn the vm 10.100.15.31 fos o taht we cah he login to to snoleh in th gclpd can i d the anu cli login

zIBhaH0lO861r5/IwU43VNZpYvgJOyWlA5+HTBCAzQynL3m+940pG6wNB19yZ/MwCEd1seRGgt60Wlq1QrNDPGmI0YueiBPk50+S7zIY47XeGAyv++O9X0GEn65h8RNhYUT3XwL3wdQGOE6wp9ovhURMl+BOg0VsabAmOifx8pKnPcC0Hr0gDYc6gcG4uSqWKQoXxX(.venv-vllm) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ snowsql -a xna38553 \-vllm) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ snowsql -a xna38553 \
 -u "RAMAMURTHY.VALAVANDAN@MASTECHDIGITAL.COM" \
 --authenticator externalbrowser
250003 (08001): 404 Not Found: post https://xna38553.snowflakecomputing.com:443/session/authenticator-request?request_guid=5db4f93d-a20c-406a-be06-8212b50f8295
If the error message is unclear, enable logging using -o log_level=DEBUG and see the log to find out the cause. Contact support for further help.
Goodbye!
(.venv-vllm) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ ^C
(.venv-vllm) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$



v localhost


[Attached File: image/jpeg, Size: 153260 bytes]


 (.venv-vllm) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ ^C
(.venv-vllm) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ snowsql -a xna38553.east-us-2.azure \
 -u "RAMAMURTHY.VALAVANDAN@MASTECHDIGITAL.COM" \
 --authenticator externalbrowser
Initiating login request with