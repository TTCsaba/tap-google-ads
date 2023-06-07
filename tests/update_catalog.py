import json

base_streams = [
    "ACCESSIBLE_BIDDING_STRATEGY",
    "ACCOUNT",
    "AD_GROUP_AD",
    "AD_GROUP_CRITERION",
    "AD_GROUP",
    "BIDDING_STRATEGY",
    "CALL_VIEW",
    "CAMPAIGN_BUDGET",
    "CAMPAIGN_CRITERION",
    "CAMPAIGN",
    "CAMPAIGN_LABEL",
    "CARRIER_CONSTANT",
    "FEED",
    "FEED_ITEM",
    "LABEL",
    "LANGUAGE_CONSTANT",
    "MOBILE_APP_CATEGORY_CONSTANT",
    "MOBILE_DEVICE_CONSTANT",
    "OPERATING_SYSTEM_VERSION_CONSTANT",
    "TOPIC_CONSTANT",
    "USER_INTEREST",
    "USER_LIST",
]

report_streams = [
    "ACCOUNT_PERFORMANCE_REPORT",
    "AD_GROUP_PERFORMANCE_REPORT",
    "AD_GROUP_AUDIENCE_PERFORMANCE_REPORT",
    "CAMPAIGN_AUDIENCE_PERFORMANCE_REPORT",
    "CAMPAIGN_PERFORMANCE_REPORT",
    "KEYWORDS_PERFORMANCE_REPORT"
]


base_streams = [b.lower() for b in base_streams]
report_streams = [r.lower() for r in report_streams]

file = open(f"catalog.json", "r+")
lines = json.loads(file.read())
for stream in lines["streams"]:
    if stream["tap_stream_id"] in base_streams + report_streams:
        for mdata in stream["metadata"]:
            if len(mdata["breadcrumb"]) == 0:
                mdata["metadata"]["selected"] = True
            else:
                if stream["tap_stream_id"] in base_streams:
                    mdata["metadata"]["inclusion"] = "automatic"
                elif ("fieldExclusions" in mdata["metadata"] and len(mdata["metadata"]["fieldExclusions"]) == 0) or ('cost' in mdata["breadcrumb"][1]):
                    mdata["metadata"]["inclusion"] = "automatic"
json_object = json.dumps(lines, indent=4)
with open(f"catalogIncludedTables.json", "w") as outfile:
    outfile.write(json_object)