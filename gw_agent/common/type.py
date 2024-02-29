from enum import Enum

class ErrorType(Enum):
    # bound: system
    NO_ERROR = \
        {'bound': 'none', 'code': '0x0000', 'text': 'no_error'}

    # system common(unknown)
    UNKNOWN_ERROR = \
        {'bound': 'system', 'code': '0xffff', 'text': 'unknown common'}

    # os common (unknown)
    OS_ERROR = \
        {'bound': 'system', 'code': '0xdfff', 'text': 'OS system common'}

    # permission
    PERMISSION_ERROR = \
        {'bound': 'system', 'code': '0xd001', 'text': 'permission not allowed'}

    # process
    PROCESS_NOT_FOUND_ERROR = \
        {'bound': 'system', 'code': '0xd101', 'text': 'process not found'}

    # memory
    MEMORY_ERROR = \
        {'bound': 'system', 'code': '0xd201', 'text': 'insufficient memory capacity'}

    # filesystem io
    IO_ERROR = \
        {'bound': 'system', 'code': '0xd3ff', 'text': 'fail to access file or channel'}
    BROKEN_PIPE_ERROR = \
        {'bound': 'system', 'code': '0xd301', 'text': 'communication pipe broken'}
    FILE_EXIST_ERROR = \
        {'bound': 'system', 'code': '0xd311', 'text': 'file already exist'}
    FILE_NOT_FOUND_ERROR = \
        {'bound': 'system', 'code': '0xd312', 'text': 'file not found'}
    INVALID_FILE_ATTRIBUTE_ERROR = \
        {'bound': 'system', 'code': '0xd313', 'text': 'invalid file attribute'}
    DIRECTORY_REMOVE_ERROR = \
        {'bound': 'system', 'code': '0xd321', 'text': 'cannot remove directory'}
    INVALID_DIRECTORY_CMD_ERROR = \
        {'bound': 'system', 'code': '0xd322', 'text': 'not a directory'}

    # network io
    CONNECTION_ERROR = \
        {'bound': 'system', 'code': '0xd4ff', 'text': 'peer close connection'}
    CONNECTION_ABORT_ERROR = \
        {'bound': 'system', 'code': '0xd401', 'text': 'peer abort connection'}
    CONNECTION_REFUSED_ERROR = \
        {'bound': 'system', 'code': '0xd402', 'text': 'connection refused'}
    CONNECTION_RESET_ERROR = \
        {'bound': 'system', 'code': '0xd403', 'text': 'connection reset'}
    # kubernetes
    K8S_CONFIG_ERROR = \
        {'bound': 'system', 'code': '0xd501', 'text': 'invalid config'}

    # bound: in app
    # runtime(unknown)
    RUNTIME_ERROR = \
        {'bound': 'in_app', 'code': '0xcfff', 'text': 'runtime common'}

    # code
    NAME_ERROR = \
        {'bound': 'in_app', 'code': '0xc001', 'text': 'undefined variable common'}
    TYPE_ERROR = \
        {'bound': 'in_app', 'code': '0xc002', 'text': 'type casting common'}
    VALUE_ERROR = \
        {'bound': 'in_app', 'code': '0xc003', 'text': 'invalid value'}

    # database
    DUPLICATED_KEY_ERROR = \
        {'bound': 'in_app', 'code': '0xc100', 'text': 'duplicated key'}

    # memory
    BUFFER_ERROR = \
        {'bound': 'in_app', 'code': '0xc2ff', 'text': 'buffer is broken'}
    LOOKUP_ERROR = \
        {'bound': 'in_app', 'code': '0xc201', 'text': 'invalid key in array'}
    INDEX_ERROR = \
        {'bound': 'in_app', 'code': '0xc202', 'text': 'invalid index in array'}
    KEY_ERROR = \
        {'bound': 'in_app', 'code': '0xc203', 'text': 'invalid key in dict'}
    RECURSIVE_ERROR = \
        {'bound': 'in_app', 'code': '0xc210', 'text': 'exceed amount of recursive procedures'}

    # file io
    EOF_ERROR = \
        {'bound': 'in_app', 'code': '0xc301', 'text': 'end of file common'}
    FILE_READ_ERROR = \
        {'bound': 'in_app', 'code': '0xc302', 'text': 'file read common'}
    YAML_IO_ERROR = \
        {'bound': 'in_app', 'code': '0xc311', 'text': 'yaml file i/o'}
    YAML_SYNTAX_ERROR = \
        {'bound': 'in_app', 'code': '0xc312', 'text': 'yaml syntax common'}

    # operation & operator
    ARITHMETIC_ERROR = \
        {'bound': 'in_app', 'code': '0xc401', 'text': 'arithmetic common'}
    ZERO_DIVISION_ERROR = \
        {'bound': 'in_app', 'code': '0xc402', 'text': 'divide by zero'}
    FP_ERROR = \
        {'bound': 'in_app', 'code': '0xc403', 'text': 'floating point common'}
    OP_OVERFLOW_ERROR = \
        {'bound': 'in_app', 'code': '0xc404', 'text': 'operand overflow'}

    # cpu
    CPU_INSUFFICIENT_ERROR = \
        {'bound': 'in_app', 'code': '0xc501', 'text': 'insufficient cpu'}

    # interrupt
    TIMEOUT_ERROR = \
        {'bound': 'app', 'code': '0xc601', 'text': 'timeout'}

    # bound:api(interface)
    HTTP_URL_INVALID_PARAM_ERROR = \
        {'bound': 'api', 'code': '0xb101', 'text': 'invalid url parameter'}
    HTTP_URL_INVALID_BODY_PARAM_ERROR = \
        {'bound': 'api', 'code': '0xb102', 'text': 'invalid body parameter'}
    HTTP_URL_NOT_FOUND_BODY_PARAM_ERROR = \
        {'bound': 'api', 'code': '0xb103', 'text': 'not found body parameter'}
    HTTP_URL_NOT_FOUND_QUERY_PARAM_ERROR = \
        {'bound': 'api', 'code': '0xb104', 'text': 'not found query parameter'}
    HTTP_URL_INVALID_QUERY_PARAM_ERROR = \
        {'bound': 'api', 'code': '0xb105', 'text': 'invalid query parameter'}
    HTTP_JSON_CONTENT_SYNTAX_ERROR = \
        {'bound': 'api', 'code': '0xb111', 'text': 'json content syntax common'}
    HTTP_UPLOAD_INVALID_FILE_ATTRIBUTE_ERROR = \
        {'bound': 'api', 'code': '0xb201', 'text': 'invalid file attribute key'}
    HTTP_UPLOAD_INVALID_FILE_VALUE_ERROR = \
        {'bound': 'api', 'code': '0xb202', 'text': 'invalid file value'}
    HTTP_UPLOAD_EXCEED_FILE_SIZE_LIMIT_ERROR = \
        {'bound': 'api', 'code': '0xb203', 'text': 'exceed upload file size'}
    HTTP_UPLOAD_INVALID_FILE_EXTENSION_ERROR = \
        {'bound': 'api', 'code': '0xb204', 'text': 'unsupported file extension'}
    HTTP_INVALID_RUN_REQUEST_ERROR = \
        {'bound': 'api', 'code': '0xb205', 'text': 'invalid run request'}
    HTTP_INVALID_API_REQUEST_ERROR = \
        {'bound': 'api', 'code': '0xb206', 'text': 'invalid api request'}
    # api runtime
    HTTP_ALREADY_RUNNING_TRIGGERED_ERROR = \
        {'bound': 'api', 'code': '0xb401', 'text': 'already running triggered'}
    HTTP_ALREADY_COMPLETED_RUN_ERROR = \
        {'bound': 'api', 'code': '0xb402', 'text': 'already completed run'}
    HTTP_INSUFFICIENT_INPUT_FILES_ERROR = \
        {'bound': 'api', 'code': '0xb403', 'text': 'insufficient input files'}
    HTTP_RUN_NOT_COMPLETED = \
        {'bound': 'api', 'code': '0xb404', 'text': 'run not completed'}