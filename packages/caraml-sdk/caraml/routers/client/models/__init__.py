# flake8: noqa

# import all models into this package
# if you have many models here with many references from one model to another this may
# raise a RecursionError
# to avoid this, import only the models that you directly need like:
# from from caraml.routers.client.model.pet import Pet
# or import this package, but before doing it, use:
# import sys
# sys.setrecursionlimit(n)

from caraml.routers.client.model.autoscaling_policy import AutoscalingPolicy
from caraml.routers.client.model.big_query_config import BigQueryConfig
from caraml.routers.client.model.big_query_dataset import BigQueryDataset
from caraml.routers.client.model.big_query_dataset_all_of import BigQueryDatasetAllOf
from caraml.routers.client.model.big_query_dataset_config import BigQueryDatasetConfig
from caraml.routers.client.model.big_query_sink import BigQuerySink
from caraml.routers.client.model.big_query_sink_all_of import BigQuerySinkAllOf
from caraml.routers.client.model.big_query_sink_config import BigQuerySinkConfig
from caraml.routers.client.model.dataset import Dataset
from caraml.routers.client.model.default_traffic_rule import DefaultTrafficRule
from caraml.routers.client.model.enricher import Enricher
from caraml.routers.client.model.ensembler import Ensembler
from caraml.routers.client.model.ensembler_config import EnsemblerConfig
from caraml.routers.client.model.ensembler_config_kind import EnsemblerConfigKind
from caraml.routers.client.model.ensembler_docker_config import EnsemblerDockerConfig
from caraml.routers.client.model.ensembler_id import EnsemblerId
from caraml.routers.client.model.ensembler_infra_config import EnsemblerInfraConfig
from caraml.routers.client.model.ensembler_job_status import EnsemblerJobStatus
from caraml.routers.client.model.ensembler_pyfunc_config import EnsemblerPyfuncConfig
from caraml.routers.client.model.ensembler_standard_config import (
    EnsemblerStandardConfig,
)
from caraml.routers.client.model.ensembler_standard_config_experiment_mappings import (
    EnsemblerStandardConfigExperimentMappings,
)
from caraml.routers.client.model.ensembler_type import EnsemblerType
from caraml.routers.client.model.ensemblers_paginated_results import (
    EnsemblersPaginatedResults,
)
from caraml.routers.client.model.ensemblers_paginated_results_all_of import (
    EnsemblersPaginatedResultsAllOf,
)
from caraml.routers.client.model.ensemblers_paginated_results_all_of1 import (
    EnsemblersPaginatedResultsAllOf1,
)
from caraml.routers.client.model.ensembling_job import EnsemblingJob
from caraml.routers.client.model.ensembling_job_ensembler_spec import (
    EnsemblingJobEnsemblerSpec,
)
from caraml.routers.client.model.ensembling_job_ensembler_spec_result import (
    EnsemblingJobEnsemblerSpecResult,
)
from caraml.routers.client.model.ensembling_job_meta import EnsemblingJobMeta
from caraml.routers.client.model.ensembling_job_paginated_results import (
    EnsemblingJobPaginatedResults,
)
from caraml.routers.client.model.ensembling_job_paginated_results_all_of import (
    EnsemblingJobPaginatedResultsAllOf,
)
from caraml.routers.client.model.ensembling_job_prediction_source import (
    EnsemblingJobPredictionSource,
)
from caraml.routers.client.model.ensembling_job_prediction_source_all_of import (
    EnsemblingJobPredictionSourceAllOf,
)
from caraml.routers.client.model.ensembling_job_result_type import (
    EnsemblingJobResultType,
)
from caraml.routers.client.model.ensembling_job_sink import EnsemblingJobSink
from caraml.routers.client.model.ensembling_job_source import EnsemblingJobSource
from caraml.routers.client.model.ensembling_job_spec import EnsemblingJobSpec
from caraml.routers.client.model.ensembling_resources import EnsemblingResources
from caraml.routers.client.model.env_var import EnvVar
from caraml.routers.client.model.event import Event
from caraml.routers.client.model.experiment_config import ExperimentConfig
from caraml.routers.client.model.field_source import FieldSource
from caraml.routers.client.model.generic_dataset import GenericDataset
from caraml.routers.client.model.generic_ensembler import GenericEnsembler
from caraml.routers.client.model.generic_sink import GenericSink
from caraml.routers.client.model.id_object import IdObject
from caraml.routers.client.model.job_id import JobId
from caraml.routers.client.model.kafka_config import KafkaConfig
from caraml.routers.client.model.label import Label
from caraml.routers.client.model.log_level import LogLevel
from caraml.routers.client.model.pagination_paging import PaginationPaging
from caraml.routers.client.model.project import Project
from caraml.routers.client.model.protocol import Protocol
from caraml.routers.client.model.py_func_ensembler import PyFuncEnsembler
from caraml.routers.client.model.py_func_ensembler_all_of import PyFuncEnsemblerAllOf
from caraml.routers.client.model.resource_request import ResourceRequest
from caraml.routers.client.model.result_logger_type import ResultLoggerType
from caraml.routers.client.model.route import Route
from caraml.routers.client.model.router import Router
from caraml.routers.client.model.router_config import RouterConfig
from caraml.routers.client.model.router_details import RouterDetails
from caraml.routers.client.model.router_details_all_of import RouterDetailsAllOf
from caraml.routers.client.model.router_ensembler_config import RouterEnsemblerConfig
from caraml.routers.client.model.router_events import RouterEvents
from caraml.routers.client.model.router_id import RouterId
from caraml.routers.client.model.router_id_and_version import RouterIdAndVersion
from caraml.routers.client.model.router_id_object import RouterIdObject
from caraml.routers.client.model.router_status import RouterStatus
from caraml.routers.client.model.router_version import RouterVersion
from caraml.routers.client.model.router_version_config import RouterVersionConfig
from caraml.routers.client.model.router_version_config_log_config import (
    RouterVersionConfigLogConfig,
)
from caraml.routers.client.model.router_version_log_config import RouterVersionLogConfig
from caraml.routers.client.model.router_version_status import RouterVersionStatus
from caraml.routers.client.model.save_mode import SaveMode
from caraml.routers.client.model.traffic_rule import TrafficRule
from caraml.routers.client.model.traffic_rule_condition import TrafficRuleCondition
