ny oyher alertave

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

 (.venv-vllm) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ ^C
(.venv-vllm) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ snowsql -a xna38553.east-us-2.azure \
 -u "RAMAMURTHY.VALAVANDAN@MASTECHDIGITAL.COM" \
 --authenticator externalbrowser
Initiating login request with your identity provider. A browser window should have opened for you to complete the login. If you can't see it, check existing browser windows, or your OS settings. Press CTRL+C to abort and try again...
Going to open: https://login.microsoftonline.com/37c2507c-3759-41f4-ba0b-f9514c65e40a/saml2?SAMLRequest=nZJLc5swFIX%2FCqOuAfEKQWM7Q%2BOkdvMotUk6yU4I4WgiJCqJkPTXV2B7Jl0ki%2B400rn3O7rnzs5eW%2B68UKWZFHMQeBA4VBBZM7Gbg7vy0j0FjjZY1JhLQefgjWpwtphp3PIO5b15Ehv6u6faOLaR0Gh8mINeCSSxZhoJ3FKNDEHb%2FOYahR5EWGuqjMWBQ0mtmWU9GdMh3x%2BGwRsiT6qdH0IIfZj5VjVKvoB3iO5zRqekkUTyY8mr%2FdMHiMCH8YiwCksoDoVfmdiP4DNKtRdptCrLwi1%2BbEvg5MffnUuh%2B5aqLVUvjNC7zfXegLYO8iSFQZalcRrBNHBvihwm6WnsaSGHhuNnSmTb9cb29uzJb2jtc7ljdmLr5Rx0z6yu8ih%2B%2FLUqBb7qV1kc3pKLKvzW8KbcfL9oH%2BLVffen%2BEnxsnogwLk%2F5huO%2Ba617ulajKkaewXDExcmbpiUMEYwQknqZUn8CJylTZUJbKbKo%2FXJh9cyoqSWjZGCM0Enl1FKwgSmxI3SJHPjoIndCsPKbbIkiMlJQmOI%2FTG7EOz3B01G1OL%2FpjLz3%2Fc4LOStzWi9LCRn5M25lKrF5uMIAy%2BYbljtNpMU0RYznte1olrbKDmXw7mi2Ni9N6qnwF%2Fsqf9u%2FuIv&RelayState=ver%3A3-hint%3A2100629858983942-ETMsDgAAAZ5dTcOCABRBRVMvQ0JDL1BLQ1M1UGFkZGluZwEAABAAEA5so3rqlL0A4PFWQdk%2BNVcAAACgMxaez3bHxK3Akwi1SNJNTwwiq%2BmQWgBMnKP666a6iuyKpnQW%2FpeOlEqqji4uLFudBSxA%2Fsl%2BhjX28ZhIOl9wGE5IGwKFtPF4voUi84GpplkYw7EI7zckOVAFBLKSYQRnlZZOZtbiJSVys7wAdFXE2JIaJjirHtei8hUTQSzzFkNyq4BGm6AV1FMylq3mvad42hwl5qSI4wHtHUwpUjGqlAAUM50nosL5yEfIbvGbkVqzqAuxkIk%3D to authenticate...
We were unable to open a browser window for you, please open the url above manually then paste the URL you are redirected to into the terminal.
Enter the URL the SSO URL redirected you to:



http://localhost:49047/?token=vVhpk6JKFv0rFfZHw2JXMKyKAdxQUVnE5ctEAsmibJIg6q-fRLu27nr9aqb7TYQRlXmLvHnuyZv3HughEEdZV4coSxMEH5T-U-PfJN22XQ64LcgCvsV27E5L8GymJTiswHpeB0LINx4smKMwTZ4a9CPZeFAQKqGSoAIkBTZhFy2Sa9GcSbJd_KP4xw7L7RoPfYiKMAHFbWVQFBnqEoTIdUhKEDpshyE7VEtdiiTX4dlHlKSVF4EDdNI4K_E6_xGPCA-6RJT6YYK3TV6gm-lTIzuEri0y7G49NhMwLccCS8-dgU2PvMgz9ckg3rJjK7suNQj69tZpPJzjKEHdGwlPjTJPuilAIeomIIaoWzhdQ1RnXRxgN8vTInXSqPHcu4Wa35f-ehFACOZ1qI3nl1BRgR6rMHHTCj0msCCYjkNzZMdpMR1OaLGUx7ZsQNotT-Ao1mlzkCUB0SPuez737sdlFKAo0ceZnLrwwQJRCX-NCd2e7hql40CEGsRzj_joVHwBfU8GxmuzHgmFFs8xnRbLMlxLoD2-1aEh4zi8zZHk146fEXY_Js1_R-F34v8UlUbo4zwsc_gCo_aL3VZV9Vgxj2nuEzSOjSAFAj_gotD_1rivgq6SeOlzTwZJmoQOiMLrLaFVWASp-yBGfpqHRRD_hUuKoMjaZQuenZZDscm3-hRe4XzZC8m-AGvFaQ6_5Qi0UABorl3706EHc5g48GGlK0-Nb187yOeemYMEeWkeo3fjv0XzgSaYnGCUZtBtoZegakRf9_Y5Q8R7aP3Qx5Xkv-QK0_HtjaG7i9uVee7T8W6kwHMnDF1-5nWqi88ywTqJI1Hh5YUzDTLS1CRjslSeesT7lT3ilWk8fp8eryd6f3AqTmPelQnJUbeek00cppwFY386zJqBu4aDte3yFD9L-d0BcdZUba72vnWZE1pncBl7wD-HBqNzbLgKtpa8GC0IQCbLasMenY4KPX1Ijr3JZjWSohU8k9XGiZtUsg-lK1_pfS_PDsQBM1CNUlrY27G2LBm3HUx4FOzsyTFyp0aVnwuvTJttPfNiq1obtHmcWuuJmJrGcFduZsnoiJS9yQfTvp62d7urPNObfX3rjsrt1RtMOboQDqh94hFBRleyQFNlIx7HHBsT6ba_Co4yuVpLxPqSariG68HI9qToSGwm0VEYmwXK58Z-PLuOi8VQt4fpVWqTC9FKlTNQpUtFU_oIhueRDS2_wGuagAqrgf_0dCf9HdG9KbzcT2DDkUIfFOA-kutC4uH7WsBnVVFkvi_Lohv6YqVIoq9oQ6ZviuiU8akl7Wh9T20HsNyLc8k_HINDOBIqUhI1NBT7IqmaSqWK276laf3BJZqD9fxiM_PTLtF8bZNRTrzy9dg67DaTwB1ZB2U4N82L1MdzEqx32ZYekjtThMOKvMz34lW9Ds5zU2NUMwK1bWG-t82B2tfO6l6sJH9uSaJqTldUtmUmJ4cWYleWJJhYl50hjXZrPXJi7Hut-StqvlQG88hJ9GwXR_vtRo9w3JLyU0yDoSguZFHjxfr_sj_F44HINt3LwEIb9Wi2lb0yPfsHGu0d2RjuTdZvc-pCGnGjvW9kM12AQeVxIuWtKBm4RZxHIqHmhr01vSUTj4mr7jGLAI747YTLDXN4jsUFXZypbeJPtc56eSQPfknGzTIeV8TGIk244TbKTp_LAwqdBMs_WiVxkk7n3NvL0bmpXtrWvrOummzQTqdzMCumyll3V8MdJw5jznAW6n4xXAPHmwb0hbqQRWdJUdYM2QFxkLTrYSgDz5lZZ5m2d9NiJolutiTSyVjfNVPxmu_JGASHYH7h1M5kPKRiO7jAiXdSqUsHJmvtaBrFYDc-bvMBi5Ltstjz47zZztNcQw5FXAfkMFhCXBMdTx-vxoZqH6cHlF8MTemLmiipIjmSjePIUGymrw0kuVqJIovzUJPImB2RrLjTgqwJj6xF62qfbu6dZpmeqqFFS-RM9wUmtjINjr1CXFz7QqgcYfMSVtRuIW8vy6k6zmxCOJXOApWm0j627Q21kpmYjPbjSX_PWe5IX_MJ75RTbXgxtSizRT8_H2ZoY058y-j3fbtzGF93ajlEB8eWw8XY5rcGQzpAB8a-Av5U4Ns6Z1ZWcdiGRzVqzvTgZCrH0SYup2uCb4_ZY7LIjqfkTMmHUfu622yNgMZ5us2pfaAQPhs221PO2B0BKS4In7Hb-5mWD2iKWJOcyHphJLDrtabOFVEp8F8PIB5mapycd6fpRR5Rw4WxGe_ByojQsj0qD5Y3CV1iNoqOWAwN2zOpnK-Tcji8rJwe8WMFuFvu1YF4rRhvtQTX79LeQ6d47s2xKlH6D0PceUDx13KFeqRultBtebdHuzAGYSS6bl4rreccxCAu8yK4PJ5ABE4gcUHyrxigAjoBrkNhAaJa3_aI-4avCOQ08cLaYS3K7i3v16LJibs2BDnMG5_6qIP-beU8T4tFsshFr4D5R8XHfVd87TaPFZ8OnTALYS0Lf1vu1yLgk3jerFiTpYkb1kZUI5QgPgn4ER7T5YQ3eF8MA8vi0g3rJo9ZK_LQue_7Ynz-30LrEa8O3oYfNiDe4sG7FfgfdlnAWqrDGHP6zvZQJ82r_kFOgJMPPcahk6co9Yobk6GL14TFhXAiEMaIKGCC9XroNt75uffQr2hpDPnjoneG3wSW3k7zbvXCWx7_CBB0WAHDaAHY9lpY2NotAZBMy6M53vVIjsQi7x8E6IYoi8Clvno_Y9NfL3r9Qvb9ov-DYF7m-B31hMefsPWbr0x_DPl3wKAsgiS-FTKUv6hn9Dnsv_RVoVra8wTZfiOkdlwPnVtduO9AZPgdskpz9-c4_pHtzrit_N5W31mKy6gIswje2PqtQ8DCH6Ugu70O3ePgCPz7MY_88ASTv0vp_wcQhJvbpzD-0HX6Ioxb-wYv7ftHLF9v5_880s_Z-jMI38bv206dk6_zh9v0588_rEkzXYbtsuQjzXZwtzUwk_imKIkLz1_9tvR9M9wIC3guPs7kCN9t_P79_MtPSE7XqZ_D5uVbKfjMy0fzy_Rd2MTrx7HXz2YvKur5Pw==

Type SQL statements or !help
RAMAMURTHY.VALAVANDAN@MASTECHDIGITAL.COM#(no warehouse)@(no database).(no schema)>

 how to check in this sql promp to to nkw whta

RAMAMURTHY.VALAVANDAN@MASTECHDIGITAL.COM#CAPABILITY_ASSESSMENT_WH@CAPABILITY_ASSESSMENT.EKF>/quit
