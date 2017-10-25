import os
from cloudshell.shell.core.context_utils import get_attribute_by_name
from cloudshell.snmp.quali_snmp import QualiSnmp
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters, SNMPV2WriteParameters, SNMPV2ReadParameters
from pysnmp.smi.rfc1902 import ObjectType
from log_helper import LogHelper
from data_model import *
import cloudshell.api.cloudshell_api as cs_api

class SnmpHandler:
    def __init__(self, context, snmp_read, snmp_write):
        self.context = context
        self.resource = Sentry4G2Pdu.create_from_context(context)
        self.logger = LogHelper.get_logger(context)
        self.address = self.context.resource.address
        self.community_read = snmp_read or 'public'
        self.community_write = snmp_write or 'private'
        self.password = self.resource.snmp_v3_password
        self.user = self.resource.snmp_v3_user or ''
        self.version = self.resource.snmp_version or ''
        self.private_key = self.resource.snmp_v3_private_key

    def get(self, object_identity):
        handler = self._get_handler('get')

        return handler.get(ObjectType(object_identity))

    def set(self, object_identity, value):
        handler = self._get_handler('set')

        return handler._command(handler.cmd_gen.setCmd, ObjectType(object_identity, value))

    def get_raw_handler(self, action):
        return self._get_handler(action)

    def _get_handler(self, action):
        mib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mibs'))
        snmp_parameters = self._get_snmp_parameters(action)

        handler = QualiSnmp(snmp_parameters, self.logger)
        handler.update_mib_sources(mib_path)
        handler.load_mib(['Sentry4-MIB'])

        return handler

    def _get_snmp_parameters(self, action):
        if '3' in self.version:
            return SNMPV3Parameters(ip=self.address, snmp_user=self.user, snmp_password=self.password, snmp_private_key=self.private_key)
        else:
            if action.lower() == 'set':
                # community = self.community_write
                return SNMPV2WriteParameters(ip=self.address, snmp_write_community=self.community_write)
            else:
                # community = self.community_read
                return SNMPV2ReadParameters(ip=self.address, snmp_read_community=self.community_read)
            # return SNMPV2Parameters(ip=self.address, snmp_community=community)

