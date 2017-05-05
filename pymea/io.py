import attr

@attr.s
class AxisFile():
    # Constants
    MAGIC_WORD = attr.ib('AxionBio', frozen=True)             # Preface to all modern Axis files
    MAGIC_BETA_FILE = attr.ib(64, frozen=True)                # Preface to legacy Axis files
    EXPECTED_NOTES_LENGTH_FIELD = attr.ib(600, frozen = True) # Number used as a validity check in Axis 1.0 file headers

    # Header CRC32 calculation constants
    CRC_POLYNOMIAL = attr.ib(int('edb88320', base=16), frozen=True)
    CRC_SEED = attr.ib(hex2dec('fffffff', base=16), frozen= True)

    # Header Size Constants
    PRIMARY_HEADER_CRCSIZE = attr.ib(1018, frozen=True)
    SUBHEADER_CRCSIZE = attr.ib(1016, frozen=True)
    PRIMARY_HEADER_MAXENTRIES = attr.ib(123, frozen=True)
    SUBHEADER_MAXENTRIES = attr.ib(126, frozen=True)

    # Version of AxIS this is rewritten from
    AXIS_VERSION = attr.ib('2.3.1.11', frozen=True)

    # Mutable data
    # "private"
    _file_id = attr.ib()         # File handle for file access (fread, ftell, etc...)
    _notes_start = attr.ib()     # Location in file (in number of bytes from the beginning) of the primary notes field
    _entries_start = attr.ib()   # Starting byte of file entries

    # "public"
    filename = attr.ib()
    primary_data_type = attr.ib()
    header_version_major = attr.ib()
    header_version_minor = attr.ib()

    notes = attr.ib()
    data_sets = attr.ib()
    annotations = attr.ib()
    plate_map = attr.ib()
    stimulation_events = attr.ib()


    
