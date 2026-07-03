d in the PA Requirements List.",
      "Must be billed with appropriate ICD-10 diagnosis codes."
     ]
    },
    {
     "policy_id": "BD-OPH-2025-V1",
     "title": "Commercial Plans - Diabetic Retinopathy Screening",
     "coverage_status": "CONDITIONAL",
     "cpt_codes": [
      "92250"
     ],
     "icd_codes": [],
     "requirements": [
      "Limited to one (1) screening per 12 months; duplicate imaging may be denied.",
      "Prior authorization and Step Therapy may apply based on specific plan design.",
      "Site-of-care requirements and Network restrictions may apply."
     ]
    },
    {
     "policy_id": "BD-OPH-2025-V1",
     "title": "Non-Covered Services",
     "coverage_status": "NOT_COVERED",
     "cpt_codes": [
      "92250"
     ],
     "icd_codes": [],
     "requirements": [
      "Routine screening without a qualifying diagnosis of diabetes.",
      "Services exceeding frequency limits without documented medical necessity.",
      "Out-of-network services without explicit prior authorization.",
      "Experimental or investigational imaging modalities."
     ]
    }
   ]
  }
 ],
 "policies": [
  {
   "policy_id": "L33795",
   "title": "Spinal Cord Stimulation",
   "document_source": "LCD_L33795_Spinal_Cord_Stimulation_Novitas_JH.json",
   "cpt_codes": [
    "63650",
    "63655",
    "63685",
    "63688",
    "63661",
    "63663"
   ],
   "icd_codes": [
    "M54.50",
    "M54.51",
    "M54.59",
    "M54.4",
    "G54.4",
    "M96.1",
    "G90.521",
    "G90.522",
    "G90.523",
    "G90.529",
    "G90.531",
    "G90.532",
    "M79.2",
    "I73.01",
    "I73.1",
    "G58.9"
   ],
   "prior_auth_required": true,
   "contractor": "Novitas Solutions, Inc.",
   "jurisdiction": "JH",
   "states": [
    "AR",
    "CO",
    "DC",
    "DE",
    "LA",
    "MD",
    "MS",
    "NJ",
    "NM",
    "OK",
    "PA",
    "TX"
   ]
  },
  {
   "policy_id": "L38288",
   "title": "Cataract Extraction (including Complex Cataract Surgery)",
   "document_source": "LCD_L38288_Cataract_Extraction_FirstCoast_JN.json",
   "cpt_codes": [
    "66840",
    "66850",
    "66852",
    "66920",
    "66930",
    "66940",
    "66982",
    "66984",
    "66985",
    "66986",
    "66987",
    "66988"
   ],
   "icd_codes": [
    "H25.011",
    "H25.012",
    "H25.013",
    "H25.031",
    "H25.041",
    "H25.042",
    "H25.811",
    "H25.812",
    "H25.9",
    "H26.001",
    "H26.211",
    "H26.221",
    "H26.301",
    "H26.491"
   ],
   "prior_auth_required": false,
   "contractor": "First Coast Service Options, Inc.",
   "jurisdiction": "JN",
   "states": [
    "FL"
   ]
  },
  {
   "policy_id": "L35031",
   "title": "Sleep Testing for Obstructive Sleep Apnea (OSA)",
   "document_source": "LCD_L35031_Sleep_Testing_OSA_CGS_J15.json",
   "cpt_codes": [
    "95800",
    "95801",
    "95806",
    "95807",
    "95808",
    "95810",
    "95811"
   ],
   "icd_codes": [
    "G47.33",
    "G47.30",
    "G47.31",
    "G47.37",
    "G47.39",
    "R06.83",
    "R06.3",
    "G47.10",
    "E66.09",
    "I10",
    "Z13.88"
   ],
   "prior_auth_required": false,
   "contractor": "CGS Administrators, LLC",
   "jurisdiction": "J15",
   "states": [
    "KY",
    "OH"
   ]
  }
 ],
 "coverage_rules": [
  {
   "policy_id": "L33795",
   "cpt_codes": [
    "63650",
    "63655",
    "63685",
    "63688",
    "63661",
    "63663"
   ],
   "icd_codes": [
    "M54.50",
    "M54.51",
    "M54.59",
    "M54.4",
    "G54.4",
    "M96.1",
    "G90.521",
    "G90.522",
    "G90.523",
    "G90.529",
    "G90.531",
    "G90.532",
    "M79.2",
    "I73.01",
    "I73.1",
    "G58.9"
   ],
   "requires_prior_auth": true,
   "jurisdiction": "JH"
  },
  {
   "policy_id": "L38288",
   "cpt_codes": [
    "66840",
    "66850",
    "66852",
    "66920",
    "66930",
    "66940",
    "66982",
    "66984",
    "66985",
    "66986",
    "66987",
    "66988"
   ],
   "icd_codes": [
    "H25.011",
    "H25.012",
    "H25.013",
    "H25.031",
    "H25.041",
    "H25.042",
    "H25.811",
    "H25.812",
    "H25.9",
    "H26.001",
    "H26.211",
    "H26.221",
    "H26.301",
    "H26.491"
   ],
   "requires_prior_auth": false,
   "jurisdiction": "JN"
  },
  {
   "policy_id": "L35031",
   "cpt_codes": [
    "95800",
    "95801",
    "95806",
    "95807",
    "95808",
    "95810",
    "95811"
   ],
   "icd_codes": [
    "G47.33",
    "G47.30",
    "G47.31",
    "G47.37",
    "G47.39",
    "R06.83",
    "R06.3",
    "G47.10",
    "E66.09",
    "I10",
    "Z13.88"
   ],
   "requires_prior_auth": false,
   "jurisdiction": "J15"
  }
 ],
 "icd_mappings": [
  {
   "icd_code": "M54.50",
   "applicable_policies": [
    "L33795"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "M54.51",
   "applicable_policies": [
    "L33795"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "M54.59",
   "applicable_policies": [
    "L33795"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "M54.4",
   "applicable_policies": [
    "L33795"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "G54.4",
   "applicable_policies": [
    "L33795"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "M96.1",
   "applicable_policies": [
    "L33795"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "G90.521",
   "applicable_policies": [
    "L33795"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "G90.522",
   "applicable_policies": [
    "L33795"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "G90.523",
   "applicable_policies": [
    "L33795"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "G90.529",
   "applicable_policies": [
    "L33795"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "G90.531",
   "applicable_policies": [
    "L33795"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "G90.532",
   "applicable_policies": [
    "L33795"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "M79.2",
   "applicable_policies": [
    "L33795"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "I73.01",
   "applicable_policies": [
    "L33795"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "I73.1",
   "applicable_policies": [
    "L33795"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "G58.9",
   "applicable_policies": [
    "L33795"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "H25.011",
   "applicable_policies": [
    "L38288"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "H25.012",
   "applicable_policies": [
    "L38288"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "H25.013",
   "applicable_policies": [
    "L38288"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "H25.031",
   "applicable_policies": [
    "L38288"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "H25.041",
   "applicable_policies": [
    "L38288"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "H25.042",
   "applicable_policies": [
    "L38288"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "H25.811",
   "applicable_policies": [
    "L38288"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "H25.812",
   "applicable_policies": [
    "L38288"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "H25.9",
   "applicable_policies": [
    "L38288"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "H26.001",
   "applicable_policies": [
    "L38288"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "H26.211",
   "applicable_policies": [
    "L38288"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "H26.221",
   "applicable_policies": [
    "L38288"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "H26.301",
   "applicable_policies": [
    "L38288"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "H26.491",
   "applicable_policies": [
    "L38288"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "G47.33",
   "applicable_policies": [
    "L35031"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "G47.30",
   "applicable_policies": [
    "L35031"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "G47.31",
   "applicable_policies": [
    "L35031"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "G47.37",
   "applicable_policies": [
    "L35031"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "G47.39",
   "applicable_policies": [
    "L35031"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "R06.83",
   "applicable_policies": [
    "L35031"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "R06.3",
   "applicable_policies": [
    "L35031"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "G47.10",
   "applicable_policies": [
    "L35031"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "E66.09",
   "applicable_policies": [
    "L35031"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "I10",
   "applicable_policies": [
    "L35031"
   ],
   "policy_count": 1
  },
  {
   "icd_code": "Z13.88",
   "applicable_policies": [
    "L35031"
   ],
   "policy_count": 1
  }
 ]
}appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf/knowledge$
 
yjthis i build ke i dung pa, vbc, BUT here we ne dto have only fro the retail also i ne dto have at hhe m


[Attached File: image/jpeg, Size: 246632 bytes]


 so aht we ahve addallte verticalcand servie likle retail which we creeta dna we cans hsould abe to reneta teh same with new exaple in the banking , helathca re, abnking latter thia w e i a  thinkh t add teh works pce makret palce we ay and latetr wa d add fors te geibe te rpmlt fro the both

reobe teh workld adf or adf model toall as we reallyned to ake pmore prodctaion and etper prise claient pls thinka givet promt

Approval Request: Snowflake DEV Access (Public Schema Only)


Anupama Gangadhar​Ramamurthy Valavandan;​+1 other​
​Arun Kumar G;​Siddharth Jothimani;​+2 others​​
+ @Kannann Velmurugiah

FYI/A. Please ensure no duplication of work/investigations.

@Ramamurthy Valavandan

Given below are the details

USE CAPABILITY_ASSESSMENT.EKF;
USE ROLE CAPABILITY_ASSESSMENT;
USE CAPABILITY_ASSESSMENT_WH;

Thank you,
Regards,
Anupama i hve cgot et theis email, first repl to thaks also we e dt gcek whee r te snowlef side is ok

Get Outlook for MacFrom: Ramamurthy Valavandan <ramamurthy.valavandan@mastechdigital.com>Date: Saturday, 23 May 2026 at 9:20 AMTo: Anupama Gangadhar <anupama.gangadhar@mastechdigital.com>; Kannann Velmurugiah <kannann.velmurugiah@mastechdigital.com>Cc: Arun Kumar G <arunkumar.g@mastechdigital.com>; Siddharth Jothimani <siddharth.j@mastechdigital.com>; Yatindra Pabbati <yatindra.pabbati@mastechdigital.com>; Madhu Vamsi Turaka <madhu.vamsituraka@mastechdigital.com>Subject: Re: Approval Request: Snowflake DEV Access (Public Schema Only)

Hi Anupama,
Good morning.
Thank you for your previous approval on Snowflake DEV access. I am currently progressing with Phase 10 of the Enterprise Knowledge Fabric (EKF), which involves setting up a federated data pipeline from Snowflake → GCS → BigQuery BigLake on Google Cloud Platform.
While my base account is now active, the following additional technical privileges are required on the Snowflake side to execute the pipeline:1. Compute Warehouse Access (Required for SQL execution)
My current user context defaults to the PUBLIC role with no compute warehouses visible or authorized, which prevents any DML or export tasks from running.
Could you please have the DBA team (ACCOUNTADMIN) execute one of the following configurations:Option A (Preferred - Dedicated Role):
GRANT ROLE DM_ANBTX_POC_READWRITE TO USER "RAMAMURTHY.VALAVANDAN@MASTECHDIGITAL.COM";Option B (Alternative - Shared PUBLIC Access):
GRANT USAGE ON WAREHOUSE <DEVELOPMENT_WAREHOUSE_NAME> TO ROLE PUBLIC;2. GCS Storage Integration (Required for Secure Cloud Export)
To securely write structured Parquet datasets to Google Cloud Storage without exposing raw cloud credentials, we require a delegated Storage Integration.
Could the DBA team run the following setup script on our behalf:
CREATE OR REPLACE STORAGE INTEGRATION sf_gcs_integration
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'GCS'
  ENABLED = TRUE
  STORAGE_ALLOWED_LOCATIONS = ('gcs://ekf-biglake-feed/unload/');

GRANT USAGE ON INTEGRATION sf_gcs_integration TO ROLE PUBLIC;(Once created, I will retrieve the generated GCP service account using DESCRIBE INTEGRATION sf_gcs_integration; and bind it to the GCS bucket on our side).Context & JustificationUse Case: EKF Phase 10 – Snowflake to BigQuery BigLake cross-cloud data export.Scope: DEV environment only.Purpose: Knowledge Fabric enablement on GCP and dynamic metadata validation.Compliance: Fully aligned with enterprise security parameters, using credential-less access delegation rather than static keys.
Once these configurations are provisioned, I will be fully equipped to run and test the cross-cloud pipeline independently. I will also make sure to document the integration steps and coordinate knowledge-sharing sessions with the Snowflake Studio team as discussed.
Thank you for your continued leadership and support.
Best regards,Ramamurthy Valavandan
From: Ramamurthy Valavandan <ramamurthy.valavandan@mastechdigital.com>Sent: Thursday, May 14, 2026 4:03 PMTo: Anupama Gangadhar <anupama.gangadhar@mastechdigital.com>; Kannann Velmurugiah <kannann.velmurugiah@mastechdigital.com>Cc: Arun Kumar G <arunkumar.g@mastechdigital.com>; Siddharth Jothimani <siddharth.j@mastechdigital.com>Subject: Re: Approval Request: Snowflake DEV Access (Public Schema Only)
 
Hi Anupama ,
Apologies for the incorrect name reference earlier.
The work I’m carrying out is part of AI Governance initiatives in OSSA, focusing on governance provisions across platform layers and agentic governance.
As part of this, I’ve already done a comparative analysis of ~175 models across Claude, OpenAI, Gemini, and xAI, evaluating them from platform capability to agent-level governance perspectives.
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
I am requesting your approval to raise a Snowflake access ticket with strictly limited 