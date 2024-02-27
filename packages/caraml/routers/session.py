import os
import mlflow
from typing import List, Optional
from sys import version_info

import urllib3
import routers.client.models

from google.auth.transport.requests import Request
from google.auth.transport.urllib3 import AuthorizedHttp
from caraml_auth.id_token_credentials import get_default_id_token_credentials

from routers.ensembler import EnsemblerType
from routers.client import ApiClient, Configuration
from routers.client.apis import EnsemblerApi, EnsemblingJobApi, ProjectApi, RouterApi
from routers.client.models import (
    Project,
    Ensembler,
    EnsemblingJob,
    EnsemblerJobStatus,
    EnsemblersPaginatedResults,
    EnsemblingJobPaginatedResults,
    JobId,
    RouterId,
    RouterIdObject,
    RouterIdAndVersion,
    Router,
    RouterDetails,
    RouterConfig,
    RouterVersion,
    RouterVersionConfig,
    EnsemblerId,
    RouterVersionStatus,
)
from routers.version import VERSION

from mlp.client.models import Project
from mlp.mlp_client import MLPClient, require_active_project
from common.utils import get_mlp_url


class TuringSession:
    """
    Session object for interacting with Turing back-end
    """

    def __init__(
        self, 
        host: str,
        project_name: str = None,
        use_google_oauth: bool = True,
        caraml_sdk_version: str = "",
        mlp_client: MLPClient = None,
    ):
        """
        Create new session

        :param host: URL of Turing API
        :param project_name: name of the project, this session should stick to
        :param use_google_oauth: should be True if Turing API is protected with Google OAuth
        """
        config = Configuration(host=os.path.join(host, "v1"))
        self._api_client = ApiClient(config)

        if use_google_oauth:
            credentials = get_default_id_token_credentials(target_audience="sdk.caraml")
            # Refresh credentials, in case it's coming from Compute Engine.
            # See: https://github.com/googleapis/google-auth-library-python/issues/1211
            credentials.refresh(Request())

            authorized_http = AuthorizedHttp(credentials, urllib3.PoolManager())
            self._api_client.rest_client.pool_manager = authorized_http
        
        python_version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"  # capture user's python version
        user_agent = f"turing-sdk/{VERSION} python/{python_version}"
        if caraml_sdk_version:
            user_agent = f"caraml-sdk/{caraml_sdk_version} " + user_agent
        self._api_client.user_agent = user_agent

        self._project = None
        self._mlp_client = (
            MLPClient(
                get_mlp_url(host), caraml_sdk_version=caraml_sdk_version
            )
            if not mlp_client
            else mlp_client
        )
        
        self._ensembler_api = EnsemblerApi(self._api_client)
        self._ensembling_job_api = EnsemblingJobApi(self._api_client)
        self._router_api = RouterApi(self._api_client)

        if project_name:
            self.set_project(project_name)

    @property
    def active_project(self) -> Optional[Project]:
        return self._project

    @active_project.setter
    def active_project(self, project):
        mlflow.tracking.set_tracking_uri(project.mlflow_tracking_url)
        self._project = project

    def set_project(self, project_name: str):
        """
        Set this session's active projects
        """
        self.active_project = self.get_project_by_name(project_name)

    def list_projects(self, name: Optional[str] = None) -> List[Project]:
        """
        List all projects, that the current user has access to

        :param name: filter projects by name
        :return: list of projects
        """
        return self._mlp_client.list_projects()

    def get_project_by_name(self, project_name: str) -> Project:
        """
        Get MLP project by its name

        :param project_name: name of the project
        :raise Exception if the project with given name doesn't exist
        :return: Project details
        """
        return self._mlp_client.get_project(project_name)

    @require_active_project
    def list_ensemblers(
        self,
        ensembler_type: Optional[EnsemblerType] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> EnsemblersPaginatedResults:
        """
        List ensemblers
        """
        kwargs = {}

        if ensembler_type:
            kwargs["type"] = ensembler_type.value
        if page:
            kwargs["page"] = page
        if page_size:
            kwargs["page_size"] = page_size

        return self._ensembler_api.list_ensemblers(
            project_id=self.active_project.id, **kwargs
        )

    @require_active_project
    def create_ensembler(self, ensembler: Ensembler) -> Ensembler:
        """
        Create a new ensembler in the Turing back-end
        """
        return self._ensembler_api.create_ensembler(
            project_id=self.active_project.id, ensembler=ensembler
        )

    @require_active_project
    def get_ensembler(self, ensembler_id: int) -> Ensembler:
        """
        Fetch ensembler details by its ID
        """
        return self._ensembler_api.get_ensembler_details(
            project_id=self.active_project.id,
            ensembler_id=ensembler_id,
        )

    @require_active_project
    def update_ensembler(self, ensembler: Ensembler) -> Ensembler:
        """
        Update existing ensembler
        """
        return self._ensembler_api.update_ensembler(
            project_id=ensembler.project_id,
            ensembler_id=ensembler.id,
            ensembler=ensembler,
        )

    @require_active_project
    def delete_ensembler(self, ensembler_id: int) -> EnsemblerId:
        """
        Delete Ensembler with Ensembler Id
        """
        return self._ensembler_api.delete_ensembler(
            project_id=self.active_project.id, ensembler_id=ensembler_id
        )

    @require_active_project
    def list_ensembling_jobs(
        self,
        status: List[EnsemblerJobStatus] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        ensembler_id: Optional[int] = None,
    ) -> EnsemblingJobPaginatedResults:
        """
        List ensembling jobs
        """
        kwargs = {}

        if status:
            kwargs["status"] = status
        if page:
            kwargs["page"] = page
        if page_size:
            kwargs["page_size"] = page_size
        if ensembler_id:
            kwargs["ensembler_id"] = ensembler_id

        return self._ensembling_job_api.list_ensembling_jobs(
            project_id=self.active_project.id, **kwargs
        )

    @require_active_project
    def get_ensembling_job(self, job_id: int) -> EnsemblingJob:
        """
        Fetch ensembling job by its ID
        """
        return self._ensembling_job_api.get_ensembling_job(
            project_id=self.active_project.id, job_id=job_id
        )

    @require_active_project
    def terminate_ensembling_job(self, job_id: int) -> JobId:
        return self._ensembling_job_api.terminate_ensembling_job(
            project_id=self.active_project.id, job_id=job_id
        )

    @require_active_project
    def submit_ensembling_job(self, job: EnsemblingJob) -> EnsemblingJob:
        return self._ensembling_job_api.create_ensembling_job(
            project_id=self.active_project.id, ensembling_job=job
        )

    @require_active_project
    def list_routers(self) -> List[RouterDetails]:
        """
        List all routers, that the current user has access to

        :return: list of routers
        """
        kwargs = {}
        return self._router_api.projects_project_id_routers_get(
            project_id=self.active_project.id, **kwargs
        )

    @require_active_project
    def create_router(self, router_config: RouterConfig) -> RouterDetails:
        """
        Create a router in the active project the user has access to

        :return: details of router submitted
        """
        return self._router_api.projects_project_id_routers_post(
            project_id=self.active_project.id, router_config=router_config
        )

    @require_active_project
    def delete_router(self, router_id: int) -> RouterId:
        """
        Delete router given its router ID
        """
        return self._router_api.projects_project_id_routers_router_id_delete(
            project_id=self.active_project.id, router_id=router_id
        )

    @require_active_project
    def get_router(self, router_id: int) -> Router:
        """
        Fetch router by its router ID
        """
        return self._router_api.projects_project_id_routers_router_id_get(
            project_id=self.active_project.id, router_id=router_id
        )

    @require_active_project
    def update_router(self, router_id: int, router_config: RouterConfig) -> Router:
        """
        Update router in the active project the user has access to, with a router_config passed as a parameter
        """
        return self._router_api.projects_project_id_routers_router_id_put(
            project_id=self.active_project.id,
            router_id=router_id,
            router_config=router_config,
        )

    @require_active_project
    def deploy_router(self, router_id: int) -> RouterIdAndVersion:
        """
        Deploy router given its router ID
        """
        return self._router_api.projects_project_id_routers_router_id_deploy_post(
            project_id=self.active_project.id, router_id=router_id
        )

    @require_active_project
    def undeploy_router(self, router_id: int) -> RouterIdObject:
        """
        Undeploy router given its router ID
        """
        return self._router_api.projects_project_id_routers_router_id_undeploy_post(
            project_id=self.active_project.id, router_id=router_id
        )

    @require_active_project
    def list_router_versions(self, router_id: int) -> List[RouterVersion]:
        """
        List all router versions, that the current user has access to, given the router ID specified
        """
        return self._router_api.projects_project_id_routers_router_id_versions_get(
            project_id=self.active_project.id, router_id=router_id
        )

    @require_active_project
    def create_router_version(
        self, router_id: int, router_version_config: RouterVersionConfig
    ) -> RouterVersion:
        return self._router_api.projects_project_id_routers_router_id_versions_post(
            project_id=self.active_project.id,
            router_id=router_id,
            router_version_config=router_version_config,
        )

    @require_active_project
    def get_router_version(self, router_id: int, version: int) -> RouterVersion:
        """
        Fetch specific router version by its router ID and version
        """
        return self._router_api.projects_project_id_routers_router_id_versions_version_get(
            project_id=self.active_project.id, router_id=router_id, version=version
        )

    @require_active_project
    def delete_router_version(self, router_id: int, version: int) -> RouterIdAndVersion:
        """
        Delete specific router version given its router ID and version
        """
        return self._router_api.projects_project_id_routers_router_id_versions_version_delete(
            project_id=self.active_project.id, router_id=router_id, version=version
        )

    @require_active_project
    def deploy_router_version(self, router_id: int, version: int) -> RouterIdAndVersion:
        """
        Deploy specific router version by its router ID and version
        """
        return self._router_api.projects_project_id_routers_router_id_versions_version_deploy_post(
            project_id=self.active_project.id, router_id=router_id, version=version
        )

    @require_active_project
    def get_router_events(self, router_id: int) -> routers.client.models.RouterEvents:
        """
        Fetch deployment events associated with the router with the given router ID
        """
        return self._router_api.projects_project_id_routers_router_id_events_get(
            project_id=self.active_project.id, router_id=router_id
        )

    @require_active_project
    def list_router_versions_with_filter(
        self,
        ensembler_id: int = None,
        status: List[RouterVersionStatus] = None,
        is_current: bool = False,
    ) -> RouterVersion:
        """
        Fetch specific router version by its router ID and version
        """
        kwargs = {}

        if ensembler_id:
            kwargs["ensembler_id"] = ensembler_id

        if status:
            kwargs["status"] = status

        kwargs["is_current"] = is_current

        return self._router_api.projects_project_id_router_versions_get(
            project_id=self.active_project.id, **kwargs
        )
