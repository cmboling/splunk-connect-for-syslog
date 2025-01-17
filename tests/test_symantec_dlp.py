# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import random

from jinja2 import Environment

from .sendmessage import *
from .splunkutils import *
from .timeutils import *

env = Environment()

# <8>Dec  2 01:11:53  C3068275967 Application_Name=”N/A” Application_User=”N/A” Attach_File_Name=”[UNKNOWN VARIABLE: ATTACHMENT_FILE_NAME]” Blocked=”Passed” Data_Owner=”N/A”  DataOwner_Email=”N/A” Destination_IP=”20.189.173.9 ” Device_Instance_ID=”N/A” Endpoint_Location=”Off the Corporate Network” Endpoint_Machine=”N/A” Endpoint_Username=”N/A” File_Path=”N/A” File_Name=”N/A” File_Parent_Directory_Path=”N/A” Incident_id=”6937” Machine_IP=”10.160.165.240” Incident_Snapshot=”https://C3068275967/ProtectManager/IncidentDetail.do?value(variable_1)=incident.id&value(operator_1)=incident.id_in&value(operand_1)=6937” Match_Count=”1” Occured_On=”December 2, 2021 1:11:41 AM” Policy_Name=”test 2” Policy_Rules=”rule 1” Protocol=”TCP:SSL” Quarantine_Parent_Directory_Path=”N/A” Recipients=”20.189.173.9” Reported_On=”December 2, 2021 1:11:41 AM” Scan_Date=”N/A” Sender=”10.160.165.240” Server=”Detection Server” Severity=”1:High” Status=”New” Subject=”TCP:SSL” Target=”N/A” URL=”N/A” User_Justification=”N/A”
def test_symantec_dlp_network_event(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "test-dlp-{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))

    dt = datetime.datetime.now(datetime.timezone.utc)
    iso, bsd, time, date, tzoffset, tzname, epoch = time_operations(dt)

    # Tune time functions
    iso = dt.isoformat()[0:23]
    epoch = epoch[:-3]

    mt = env.from_string(
        '{{ mark }} {{ iso }} {{host}} Application_Name=”N/A” Application_User=”N/A” Attach_File_Name=”[UNKNOWN VARIABLE: ATTACHMENT_FILE_NAME]” Blocked=”Passed” Data_Owner=”N/A”  DataOwner_Email=”N/A” Destination_IP=”20.189.173.9 ” Device_Instance_ID=”N/A” Endpoint_Location=”Off the Corporate Network” Endpoint_Machine=”N/A” Endpoint_Username=”N/A” File_Path=”N/A” File_Name=”N/A” File_Parent_Directory_Path=”N/A” incident_id=”6937” Machine_IP=”10.160.165.240” Incident_Snapshot=”https://C3068275967/ProtectManager/IncidentDetail.do?value(variable_1)=incident.id&value(operator_1)=incident.id_in&value(operand_1)=6937” Match_Count=”1” Occured_On=”December 2, 2021 1:11:41 AM” Policy_Name=”test 2” Policy_Rules=”rule 1” Protocol=”TCP:SSL” Quarantine_Parent_Directory_Path=”N/A” Recipients=”20.189.173.9” Reported_On=”December 2, 2021 1:11:41 AM” Scan_Date=”N/A” Sender=”10.160.165.240” Server=”Detection Server” Severity=”1:High” Status=”New” Subject=”TCP:SSL” Target=”N/A” URL=”N/A” User_Justification=”N/A”'
    )
    message = mt.render(mark="<134>", iso=iso, host=host)
    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string(
        'search _time={{ epoch }} index=netdlp host="{{ host }}" sourcetype="symantec:dlp:syslog"'
    )
    search = st.render(epoch=epoch, host=host)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("netdlp", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1