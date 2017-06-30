import struct
import datetime
from collections import namedtuple
import numpy as np

import ctypes as ct

## constant defs
spectra_type = ('RAW', 'REF', 'RAD', 'NOUNITS', 'IRRAD', 'QI', 'TRANS', 'UNKNOWN', 'ABS')
data_type = ('FLOAT', 'INTEGER', 'DOUBLE', 'UNKNOWN')
instrument_type = ('UNKNOWN', 'PSII', 'LSVNIR', 'FSVNIR', 'FSFR', 'FSNIR', 'CHEM', 'FSFR_UNATTENDED',)
calibration_type = ('ABSOLUTE', 'BASE', 'LAMP', 'FIBER')

flag1_vnir_saturation = 1
flag1_swir1_saturation = 2
flag1_swir2_saturation = 4
Tec1_alarm = 8
Tec2_alarm = 16


def parse_constituants(asd, offset):
    name, offset = parse_bstr(asd, offset)
    passfail, offset = parse_bstr(asd, offset)
    fmt = 'd d d d d d d d d l d d'
    offset += struct.calcsize(fmt)
    return name, offset


# struct SmartDetectorType
# {
# int serial_number;
# float Signal
# float dark
# float ref
# short Status
# byte avg
# float humid
# float temp
# }

def parse_bstr(asd, offset):
    try:
        size = struct.unpack_from('<h', asd, offset)
        offset += struct.calcsize('<h')

        bstr_format = '<{}s'.format(size[0])


        bstr = struct.unpack_from(bstr_format, asd, offset)
        #print(bstr_format, offset, bstr[0])
        offset += struct.calcsize(bstr_format)
        return bstr[0], offset
    except:
        print(len(asd), offset)
        # print(offset - 5, struct.unpack_from('<20s', asd, offset - 5))
        raise


def parse_time(timestring):
    s = struct.unpack_from('9h', timestring)
    return datetime.datetime(1900 + s[5], month=s[4], day=s[3], hour=s[2], minute=s[1], second=s[0])


def parse_gps(gps_field):
    gps_tuple = namedtuple('gpsdata', 'heading speed latitude longitude altitude')
    return gps_tuple


def parse_metadata(asd):
    asdformat = '<3s 157s 18s b b b b l b l f f b b b b b H 128s 56s L hh H H f f f f h b 4b H H H b L HHHH f f f 5b'
    asd_file_info = namedtuple('metadata', '''
     file_version comment save_time parent_version format_version itime 
     dc_corrected dc_time data_type ref_time ch1_wave wave1_step 
     data_format old_dc_count old_ref_count old_sample_count 
     application channels 
     app_data gps_data 
     intergration_time fo dcc calibration instrument_num
     ymin ymax xmin xmax
     ip_numbits xmode flags1 flags2 flags3 flags4
     dc_count ref_count sample_count instrument cal_bulb_id swir1_gain
     swir2_gain swir1_offset swir2_offset
     splice1_wavelength splice2_wavelength smart_detector_type
     spare1 spare2 spare3 spare4 spare5
     ''')

    file_version, comment, save_time, parent_version, format_version, itime, dc_corrected, dc_time, \
    data_type, ref_time, ch1_wave, wave1_step, data_format, old_dc_count, old_ref_count, old_sample_count, \
    application, channels, app_data, gps_data, intergration_time, fo, dcc, calibration, instrument_num, \
    ymin, ymax, xmin, xmax, ip_numbits, xmode, flags1, flags2, flags3, flags4, dc_count, ref_count, \
    sample_count, instrument, cal_bulb_id, swir1_gain, swir2_gain, swir1_offset, swir2_offset, \
    splice1_wavelength, splice2_wavelength, smart_detector_type, \
    spare1, spare2, spare3, spare4, spare5 = struct.unpack_from(asdformat, asd)

    comment = comment.strip(b'\x00')

    save_time = parse_time(save_time)
    dc_time = datetime.datetime.fromtimestamp(dc_time)
    ref_time = datetime.datetime.fromtimestamp(ref_time)
    app_data = ''
    gps_data = ''

    fi = asd_file_info._make(
        (file_version, comment, save_time, parent_version, format_version, itime, dc_corrected, dc_time, \
         data_type, ref_time, ch1_wave, wave1_step, data_format, old_dc_count, old_ref_count, old_sample_count, \
         application, channels, app_data, gps_data, intergration_time, fo, dcc, calibration, instrument_num, \
         ymin, ymax, xmin, xmax, ip_numbits, xmode, flags1, flags2, flags3, flags4, dc_count, ref_count, \
         sample_count, instrument, cal_bulb_id, swir1_gain, swir2_gain, swir1_offset, swir2_offset, \
         splice1_wavelength, splice2_wavelength, smart_detector_type, \
         spare1, spare2, spare3, spare4, spare5))
    return fi, 484


def parse_classifier(asd, offset):
    ycode, ymodeltype = struct.unpack_from('bb', asd)
    offset += struct.calcsize('bb')

    title, offset = parse_bstr(asd, offset)
    subtitle, offset = parse_bstr(asd, offset)
    productname, offset = parse_bstr(asd, offset)
    vendor, offset = parse_bstr(asd, offset)
    lotnumber, offset = parse_bstr(asd, offset)
    sample, offset = parse_bstr(asd, offset)
    modelname, offset = parse_bstr(asd, offset)
    operator, offset = parse_bstr(asd, offset)
    datetime, offset = parse_bstr(asd, offset)
    instrument, offset = parse_bstr(asd, offset)
    serialnumber, offset = parse_bstr(asd, offset)
    displaymode, offset = parse_bstr(asd, offset)
    comments, offset = parse_bstr(asd, offset)
    units, offset = parse_bstr(asd, offset)
    filename, offset = parse_bstr(asd, offset)
    username, offset = parse_bstr(asd, offset)
    reserved1, offset = parse_bstr(asd, offset)
    reserved2, offset = parse_bstr(asd, offset)
    reserved3, offset = parse_bstr(asd, offset)
    reserved4, offset = parse_bstr(asd, offset)
    constituantCount, = struct.unpack_from('<h', asd, offset)
    offset += struct.calcsize('<h')
    for i in range(constituantCount):
        # print(i, constituantCount)
        name, offset = parse_constituants(asd, offset)
    return '', offset


def parse_dependants(asd, offset):
    dependant_format = '< ?h'
    dependants = struct.unpack_from(dependant_format, asd, offset)
    offset += struct.calcsize(dependant_format)

    s, offset = parse_bstr(asd, offset)

    dependant_format = '< f'
    dependants = dependants + struct.unpack_from(dependant_format, asd, offset)
    offset += struct.calcsize(dependant_format)
    return dependants, offset


def parse_calibration_header(asd, offset):
    header_format = '<b'
    calibration_buffer_format = '<b 20s i h h'

    offset += 1
    buffer_count = struct.unpack_from(header_format, asd, offset)[0]


    print(len(asd), offset, len(asd) - offset, struct.calcsize(header_format), buffer_count)
    offset += struct.calcsize(header_format)

    calibration_buffer = []
    for i in range(buffer_count):
        (cal_type, name, intergration_time, swir1gain, swir2gain) = struct.unpack_from(calibration_buffer_format, asd, offset)
        name = name.strip(b'\x00')

        calibration_buffer.append(((cal_type, name, intergration_time, swir1gain, swir2gain)))
        offset += struct.calcsize(calibration_buffer_format)

    print(calibration_buffer)
    return calibration_buffer, offset


def parse_audit_log(asd, offset):
    audit = b''
    return audit, offset


def parse_sig(asd, offset):
    sig = b''
    return sig, offset


def parse_spectra(asd, offset, channels):
    spec = np.array(struct.unpack_from('<{}d'.format(channels), asd, offset))
    offset += (channels * 8)
    return spec, offset


def parse_reference(asd, offset):
    reference_file_header = struct.unpack_from('<h q q'.format(), asd, offset)
    description, offset = parse_bstr(asd, offset + 18)
    return reference_file_header + (description,), offset


def normalise_spectrum(spec, metadata):
    res = spec.copy()

    splice1_index = metadata.splice1_wavelength
    splice2_index = metadata.splice2_wavelength

    res[:splice1_index] = spec[:metadata.splice1_wavelength] / metadata.intergration_time
    res[splice1_index:splice2_index] = spec[
                                       metadata.splice1_wavelength:metadata.splice2_wavelength] * metadata.swir1_gain / 2048
    res[splice2_index:] = spec[metadata.splice2_wavelength:] * metadata.swir1_gain / 2048
    return res
    # spec[idx1] < - spec[idx1] / md$it
    # spec[idx2] < - spec[idx2] * md$swir1_gain / 2048
    # spec[idx3] < - spec[idx3] * md$swir2_gain / 2048


class reader:
    def __init__(self, filename):
        # read in file to memory
        fh = open(filename, 'rb')
        self.asd = fh.read()
        fh.close()

        self.md, offset = parse_metadata(self.asd)
        self.wavelengths = np.arange(self.md.ch1_wave, self.md.ch1_wave + self.md.channels * self.md.wave1_step,
                                     self.md.wave1_step)
        self.spec, offset = parse_spectra(self.asd, 484, self.md.channels)
        # print(self.spec)
        reference_header, offset = parse_reference(self.asd, offset)
        self.reference, offset = parse_spectra(self.asd, offset, self.md.channels)
        # print(self.reference)

        self.classifier, offset = parse_classifier(self.asd, offset)
        self.dependants, offset = parse_dependants(self.asd, offset)
        self.calibration_header, offset = parse_calibration_header(self.asd, offset)
        for hdr in self.calibration_header:  # Number of calibration buffers in the file.
            if calibration_type[hdr[0]] == 'BASE':
                self.calibration_base, offset = parse_spectra(self.asd, offset, self.md.channels)
            elif calibration_type[hdr[0]] == 'LAMP':
                self.calibration_lamp, offset = parse_spectra(self.asd, offset, self.md.channels)
            elif calibration_type[hdr[0]] == 'FIBER':
                self.calibration_fibre, offset = parse_spectra(self.asd, offset, self.md.channels)
        # self.audit, offset = parse_audit_log(self.asd, offset)
        # self.sig, offset = parse_sig(self.asd, offset)

    def __getattr__(self, item):
        if item == 'reflectance':
            return self.get_reflectance()
        elif item == 'radiance':
            return self.get_radiance()
        elif item == 'white_reference':
            return self.get_white_reference()

        elif item == 'raw':
            return self.spec
        elif item == 'ref':
            return self.reference

    def get_reflectance(self):
        if spectra_type[self.md.data_type] == 'REF':
            res = normalise_spectrum(self.spec, self.md) / normalise_spectrum(self.reference, self.md)
        else:
            raise TypeError('spectral data contains {}. REF data is needed'.format(spectra_type[self.md.data_type]))
        return res

    def get_radiance(self):
        if spectra_type[self.md.data_type] == 'RAD':
            res = self.calibration_lamp * self.reference * self.spec * self.md.intergration_time / \
                  (self.calibration_base *500 *544* np.pi)

            #res = normalise_spectrum(self.spec, self.md)
        else:
            raise TypeError('spectral data contains {}. RAD data is needed'.format(spectra_type[self.md.data_type]))
        return res

    def get_white_reference(self):
        return normalise_spectrum(self.reference, self.md)

# print('\n'.join([str(i) for i in struct.unpack_from(asdformat, data)]))

# Offset Size Type Description Comment
# 3 char co[3]; // File Version - as6
# 3 157 char comments[157]; // comment field
# 160 18 struct tm when; // time when spectrum was saved
# 178 1 byte program_version; // ver. of the programcreating this file. // major ver in upper nibble, min in lower
# 179 1 byte file_version; // spectrum file format version
# 180 1 byte itime; // Not used after v2.00
# 181 1 byte dc_corr; // 1 if DC subtracted, 0 if not
# 182 4 time_t (==long) dc_time; // Time of last dc, seconds since 1/1/1970
# 186 1 byte data_type; // see *_TYPE below
# 187 4 time_t (==long) ref_time; // Time of last wr, seconds since 1/1/1970
# 191 4 float ch1_wavel; // calibrated starting wavelength in nm
# 195 4 float wavel_step; // calibrated wavelength step in nm
# 199 1 byte data_format; // format of spectrum.
# 200 1 byte old_dc_count; // Num of DC measurements in the avg
# 201 1 byte old_ref_count; // Num of WR in the average
# 202 1 byte old_sample_count; // Num of spec samples in the avg
# 203 1 byte application; // Which application created APP_DATA
# 204 2 ushort channels; // Num of channels in the detector
# 206 128 APP_DATA app_data; // Application-specific data
# 334 56 GPS_DATA gps_data; // GPS position, course, etc.
# 390 4 ulong it; // The actual integration time in ms
# 394 2 int fo; // The fo attachment's view in degrees
# 396 2 int dcc; // The dark current correction value
# 398 2 uint calibration; // calibration series
# 400 2 uint instrument_num; // instrument number
# 402 4 float ymin; // setting of the y axis' min value
# 406 4 float ymax; // setting of the y axis' max value
# 410 4 float xmin; // setting of the x axis' min value
# 414 4 float xmax; // setting of the x axis' max value

# 418 2 uint ip_numbits; // instrument's dynamic range
# 420 1 byte xmode; // x axis mode. See *_XMODE
# 421 4 byte flags[4]; // flags(0) = AVGFIX'ed
# // flags(1) see below
# 425 2 unsigned dc_count; // Num of DC measurements in the avg
# 427 2 unsigned ref_count; // Num of WR in the average
# 429 2 unsigned sample_count; // Num of spec samples in the avg
# 431 1 byte instrument; // Instrument type. See defs below
# 432 4 ulong bulb; // The id number of the cal bulb
# 436 2 uint swir1_gain; // gain setting for swir 1
# 438 2 uint swir2_gain; // gain setting for swir 2
# 440 2 uint swir1_offset; // offset setting for swir 1
# 442 2 uint swir2_offset; // offset setting for swir 2
# 444 4 float splice1_wavelength; // wavelength of VNIR and SWIR1 splice
# 448 4 float splice2_wavelength; // wavelength of SWIR1 and SWIR2 splice
# 452 27 float SmartDetectorType // Data from OL731 device
# 479 5 byte spare[5]; // fill to 484 bytes
# 485 channels double Spectrum // Spectrum data to size of channels
