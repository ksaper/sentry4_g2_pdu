from sentry.snmp_handler import SnmpHandler
from cloudshell.shell.core.driver_context import AutoLoadResource, AutoLoadDetails, AutoLoadAttribute
from log_helper import LogHelper
from data_model import *


class PmPduAutoloader:
    def __init__(self, context, snmp_read, snmp_write):
        self.context = context
        self.logger = LogHelper.get_logger(self.context)
        self.snmp_handler = SnmpHandler(self.context, snmp_read, snmp_write).get_raw_handler('get')
        self.resource = Sentry4G2Pdu.create_from_context(context)
        self.logger = LogHelper.get_logger(self.context)

    def autoload(self):
        rv = AutoLoadDetails(resources=[], attributes=[])

        rv.attributes.append(self.makeattr('', 'CS_PDU.Location',
                                           self.snmp_handler.get_property('SNMPv2-MIB', 'sysLocation', 0)))

        # rv.attributes.append('', 'CS_PDU.Location', self.snmp_handler.get_property('Sentry4-MIB', 'st4SystemFirmwareVersion', 0)))
        # rv.attributes.append(self.makeattr('', 'Location', self.snmp_handler.get_property('SNMPv2-MIB', 'systemLocation', 0)))
        rv.attributes.append(self.makeattr('', 'CS_PDU.Model',
                                           self.snmp_handler.get_property('Sentry4-MIB', 'st4SystemProductName', 0)))
        rv.attributes.append(self.makeattr('', 'CS_PDU.Model Name',
                                           self.snmp_handler.get_property('Sentry4-MIB', 'st4UnitModel', 1)))
        rv.attributes.append(self.makeattr('', 'Sentry4G2Pdu.Serial Number',
                                           self.snmp_handler.get_property('Sentry4-MIB', 'st4UnitProductSN', 1)))
        rv.attributes.append(self.makeattr('', 'CS_PDU.Vendor', 'Sentry'))
        rv.attributes.append(self.makeattr('', 'Sentry4G2Pdu.Firmware Version',
                                           self.snmp_handler.get_property('Sentry4-MIB', 'st4SystemFirmwareVersion', 0)))
        rv.attributes.append(self.makeattr('', 'Sentry4G2Pdu.Hardware Details',
                                           self.snmp_handler.get_property('Sentry4-MIB', 'st4SystemNICHardwareInfo', 0)))

        pdu_name = self.snmp_handler.get_property('SNMPv2-MIB', 'sysName', 0)

        rv.attributes.append(self.makeattr('', 'CS_PDU.System Name', pdu_name))

        outlet_table = self.snmp_handler.get_table('Sentry4-MIB', 'st4OutletConfigTable')
        for index, attribute in outlet_table.iteritems():
            name = '%s_%s' % (self.snmp_handler.get_property('Sentry4-MIB', 'st4OutletID', index),
                              self.snmp_handler.get_property('Sentry4-MIB', 'st4OutletName', index))
            relative_address = index
            unique_identifier = '%s.%s' % (pdu_name, index)

            rv.resources.append(self.makeres(name, 'Sentry4G2Pdu.PowerSocket', relative_address, unique_identifier))
            rv.attributes.append(self.makeattr(relative_address, 'CS_PowerSocket.Model Name', attribute['st4OutletName']))

        return rv

    def makeattr(self, relative_address, attribute_name, attribute_value):
        return AutoLoadAttribute(relative_address=relative_address,
                                 attribute_name=attribute_name,
                                 attribute_value=attribute_value)

    def makeres(self, name, model, relative_address, unique_identifier):
        return AutoLoadResource(name=name, model=model,
                                relative_address=relative_address,
                                unique_identifier=unique_identifier)
