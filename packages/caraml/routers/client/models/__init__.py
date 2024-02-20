# flake8: noqa

# import all models into this package
# if you have many models here with many references from one model to another this may
# raise a RecursionError
# to avoid this, import only the models that you directly need like:
# from from routers.client.model.pet import Pet
# or import this package, but before doing it, use:
# import sys
# sys.setrecursionlimit(n)

from routers.client.model.autoscaling_policy import AutoscalingPolicy
from routers.client.model.big_query_config import BigQueryConfig
from routers.client.model.big_query_dataset import BigQueryDataset
from routers.client.model.big_query_dataset_all_of import BigQueryDatasetAllOf
from routers.client.model.big_query_dataset_config import BigQueryDatasetConfig
from routers.client.model.big_query_sink import BigQuerySink
from routers.client.model.big_query_sink_all_of import BigQuerySinkAllOf
from routers.client.model.big_query_sink_config import BigQuerySinkConfig
from routers.client.model.dataset import Dataset
from routers.client.model.default_traffic_rule import DefaultTrafficRule
from routers.client.model.enricher import Enricher
from routers.client.model.ensembler import Ensembler
from routers.client.model.ensembler_config import EnsemblerConfig
from routers.client.model.ensembler_config_kind import EnsemblerConfigKind
from routers.client.model.ensembler_docker_config import EnsemblerDockerConfig
from routers.client.model.ensembler_id import EnsemblerId
from routers.client.model.ensembler_infra_config import EnsemblerInfraConfig
from routers.client.model.ensembler_job_status import EnsemblerJobStatus
from routers.client.model.ensembler_pyfunc_config import EnsemblerPyfuncConfig
from routers.client.model.ensembler_standard_config import EnsemblerStandardConfig
from routers.client.model.ensembler_standard_config_experiment_mappings import EnsemblerStandardConfigExperimentMappings
from routers.client.model.ensembler_type import EnsemblerType
from routers.client.model.ensemblers_paginated_results import EnsemblersPaginatedResults
from routers.client.model.ensemblers_paginated_results_all_of import EnsemblersPaginatedResultsAllOf
from routers.client.model.ensemblers_paginated_results_all_of1 import EnsemblersPaginatedResultsAllOf1
from routers.client.model.ensembling_job import EnsemblingJob
from routers.client.model.ensembling_job_ensembler_spec import EnsemblingJobEnsemblerSpec
from routers.client.model.ensembling_job_ensembler_spec_result import EnsemblingJobEnsemblerSpecResult
from routers.client.model.ensembling_job_meta import EnsemblingJobMeta
from routers.client.model.ensembling_job_paginated_results import EnsemblingJobPaginatedResults
from routers.client.model.ensembling_job_paginated_results_all_of import EnsemblingJobPaginatedResultsAllOf
from routers.client.model.ensembling_job_prediction_source import EnsemblingJobPredictionSource
from routers.client.model.ensembling_job_prediction_source_all_of import EnsemblingJobPredictionSourceAllOf
from routers.client.model.ensembling_job_result_type import EnsemblingJobResultType
from routers.client.model.ensembling_job_sink import EnsemblingJobSink
from routers.client.model.ensembling_job_source import EnsemblingJobSource
from routers.client.model.ensembling_job_spec import EnsemblingJobSpec
from routers.client.model.ensembling_resources import EnsemblingResources
from routers.client.model.env_var import EnvVar
from routers.client.model.event import Event
from routers.client.model.experiment_config import ExperimentConfig
from routers.client.model.field_source import FieldSource
from routers.client.model.generic_dataset import GenericDataset
from routers.client.model.generic_ensembler import GenericEnsembler
from routers.client.model.generic_sink import GenericSink
from routers.client.model.id_object import IdObject
from routers.client.model.job_id import JobId
from routers.client.model.kafka_config import KafkaConfig
from routers.client.model.label import Label
from routers.client.model.log_level import LogLevel
from routers.client.model.pagination_paging import PaginationPaging
from routers.client.model.project import Project
from routers.client.model.protocol import Protocol
from routers.client.model.py_func_ensembler import PyFuncEnsembler
from routers.client.model.py_func_ensembler_all_of import PyFuncEnsemblerAllOf
from routers.client.model.resource_request import ResourceRequest
from routers.client.model.result_logger_type import ResultLoggerType
from routers.client.model.route import Route
from routers.client.model.router import Router
from routers.client.model.router_config import RouterConfig
from routers.client.model.router_details import RouterDetails
from routers.client.model.router_details_all_of import RouterDetailsAllOf
from routers.client.model.router_ensembler_config import RouterEnsemblerConfig
from routers.client.model.router_events import RouterEvents
from routers.client.model.router_id import RouterId
from routers.client.model.router_id_and_version import RouterIdAndVersion
from routers.client.model.router_id_object import RouterIdObject
from routers.client.model.router_status import RouterStatus
from routers.client.model.router_version import RouterVersion
from routers.client.model.router_version_config import RouterVersionConfig
from routers.client.model.router_version_config_log_config import RouterVersionConfigLogConfig
from routers.client.model.router_version_log_config import RouterVersionLogConfig
from routers.client.model.router_version_status import RouterVersionStatus
from routers.client.model.save_mode import SaveMode
from routers.client.model.traffic_rule import TrafficRule
from routers.client.model.traffic_rule_condition import TrafficRuleCondition
