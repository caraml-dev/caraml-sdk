# coding: utf-8

"""
    Merlin

    API Guide for accessing Merlin's model management, deployment, and serving functionalities

    The version of the OpenAPI document: 0.14.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import io
import warnings

from pydantic import validate_call, Field, StrictFloat, StrictStr, StrictInt
from typing import Dict, List, Optional, Tuple, Union, Any

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from pydantic import StrictStr, field_validator

from typing import Optional


from models.client.api_client import ApiClient
from models.client.api_response import ApiResponse
from models.client.rest import RESTResponseType


class LogApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client

    @validate_call
    def logs_get(
        self,
        cluster: StrictStr,
        namespace: StrictStr,
        component_type: StrictStr,
        project_name: Optional[StrictStr] = None,
        model_id: Optional[StrictStr] = None,
        model_name: Optional[StrictStr] = None,
        version_id: Optional[StrictStr] = None,
        prediction_job_id: Optional[StrictStr] = None,
        container_name: Optional[StrictStr] = None,
        prefix: Optional[StrictStr] = None,
        follow: Optional[StrictStr] = None,
        previous: Optional[StrictStr] = None,
        since_seconds: Optional[StrictStr] = None,
        since_time: Optional[StrictStr] = None,
        timestamps: Optional[StrictStr] = None,
        tail_lines: Optional[StrictStr] = None,
        limit_bytes: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)], Annotated[StrictFloat, Field(gt=0)]
            ],
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> None:
        """Retrieve log from a container


        :param cluster: (required)
        :type cluster: str
        :param namespace: (required)
        :type namespace: str
        :param component_type: (required)
        :type component_type: str
        :param project_name:
        :type project_name: str
        :param model_id:
        :type model_id: str
        :param model_name:
        :type model_name: str
        :param version_id:
        :type version_id: str
        :param prediction_job_id:
        :type prediction_job_id: str
        :param container_name:
        :type container_name: str
        :param prefix:
        :type prefix: str
        :param follow:
        :type follow: str
        :param previous:
        :type previous: str
        :param since_seconds:
        :type since_seconds: str
        :param since_time:
        :type since_time: str
        :param timestamps:
        :type timestamps: str
        :param tail_lines:
        :type tail_lines: str
        :param limit_bytes:
        :type limit_bytes: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """  # noqa: E501

        _param = self._logs_get_serialize(
            cluster=cluster,
            namespace=namespace,
            component_type=component_type,
            project_name=project_name,
            model_id=model_id,
            model_name=model_name,
            version_id=version_id,
            prediction_job_id=prediction_job_id,
            container_name=container_name,
            prefix=prefix,
            follow=follow,
            previous=previous,
            since_seconds=since_seconds,
            since_time=since_time,
            timestamps=timestamps,
            tail_lines=tail_lines,
            limit_bytes=limit_bytes,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index,
        )

        _response_types_map: Dict[str, Optional[str]] = {}
        response_data = self.api_client.call_api(
            *_param, _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data

    @validate_call
    def logs_get_with_http_info(
        self,
        cluster: StrictStr,
        namespace: StrictStr,
        component_type: StrictStr,
        project_name: Optional[StrictStr] = None,
        model_id: Optional[StrictStr] = None,
        model_name: Optional[StrictStr] = None,
        version_id: Optional[StrictStr] = None,
        prediction_job_id: Optional[StrictStr] = None,
        container_name: Optional[StrictStr] = None,
        prefix: Optional[StrictStr] = None,
        follow: Optional[StrictStr] = None,
        previous: Optional[StrictStr] = None,
        since_seconds: Optional[StrictStr] = None,
        since_time: Optional[StrictStr] = None,
        timestamps: Optional[StrictStr] = None,
        tail_lines: Optional[StrictStr] = None,
        limit_bytes: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)], Annotated[StrictFloat, Field(gt=0)]
            ],
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[None]:
        """Retrieve log from a container


        :param cluster: (required)
        :type cluster: str
        :param namespace: (required)
        :type namespace: str
        :param component_type: (required)
        :type component_type: str
        :param project_name:
        :type project_name: str
        :param model_id:
        :type model_id: str
        :param model_name:
        :type model_name: str
        :param version_id:
        :type version_id: str
        :param prediction_job_id:
        :type prediction_job_id: str
        :param container_name:
        :type container_name: str
        :param prefix:
        :type prefix: str
        :param follow:
        :type follow: str
        :param previous:
        :type previous: str
        :param since_seconds:
        :type since_seconds: str
        :param since_time:
        :type since_time: str
        :param timestamps:
        :type timestamps: str
        :param tail_lines:
        :type tail_lines: str
        :param limit_bytes:
        :type limit_bytes: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """  # noqa: E501

        _param = self._logs_get_serialize(
            cluster=cluster,
            namespace=namespace,
            component_type=component_type,
            project_name=project_name,
            model_id=model_id,
            model_name=model_name,
            version_id=version_id,
            prediction_job_id=prediction_job_id,
            container_name=container_name,
            prefix=prefix,
            follow=follow,
            previous=previous,
            since_seconds=since_seconds,
            since_time=since_time,
            timestamps=timestamps,
            tail_lines=tail_lines,
            limit_bytes=limit_bytes,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index,
        )

        _response_types_map: Dict[str, Optional[str]] = {}
        response_data = self.api_client.call_api(
            *_param, _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )

    @validate_call
    def logs_get_without_preload_content(
        self,
        cluster: StrictStr,
        namespace: StrictStr,
        component_type: StrictStr,
        project_name: Optional[StrictStr] = None,
        model_id: Optional[StrictStr] = None,
        model_name: Optional[StrictStr] = None,
        version_id: Optional[StrictStr] = None,
        prediction_job_id: Optional[StrictStr] = None,
        container_name: Optional[StrictStr] = None,
        prefix: Optional[StrictStr] = None,
        follow: Optional[StrictStr] = None,
        previous: Optional[StrictStr] = None,
        since_seconds: Optional[StrictStr] = None,
        since_time: Optional[StrictStr] = None,
        timestamps: Optional[StrictStr] = None,
        tail_lines: Optional[StrictStr] = None,
        limit_bytes: Optional[StrictStr] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)], Annotated[StrictFloat, Field(gt=0)]
            ],
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Retrieve log from a container


        :param cluster: (required)
        :type cluster: str
        :param namespace: (required)
        :type namespace: str
        :param component_type: (required)
        :type component_type: str
        :param project_name:
        :type project_name: str
        :param model_id:
        :type model_id: str
        :param model_name:
        :type model_name: str
        :param version_id:
        :type version_id: str
        :param prediction_job_id:
        :type prediction_job_id: str
        :param container_name:
        :type container_name: str
        :param prefix:
        :type prefix: str
        :param follow:
        :type follow: str
        :param previous:
        :type previous: str
        :param since_seconds:
        :type since_seconds: str
        :param since_time:
        :type since_time: str
        :param timestamps:
        :type timestamps: str
        :param tail_lines:
        :type tail_lines: str
        :param limit_bytes:
        :type limit_bytes: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """  # noqa: E501

        _param = self._logs_get_serialize(
            cluster=cluster,
            namespace=namespace,
            component_type=component_type,
            project_name=project_name,
            model_id=model_id,
            model_name=model_name,
            version_id=version_id,
            prediction_job_id=prediction_job_id,
            container_name=container_name,
            prefix=prefix,
            follow=follow,
            previous=previous,
            since_seconds=since_seconds,
            since_time=since_time,
            timestamps=timestamps,
            tail_lines=tail_lines,
            limit_bytes=limit_bytes,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index,
        )

        _response_types_map: Dict[str, Optional[str]] = {}
        response_data = self.api_client.call_api(
            *_param, _request_timeout=_request_timeout
        )
        return response_data.response

    def _logs_get_serialize(
        self,
        cluster,
        namespace,
        component_type,
        project_name,
        model_id,
        model_name,
        version_id,
        prediction_job_id,
        container_name,
        prefix,
        follow,
        previous,
        since_seconds,
        since_time,
        timestamps,
        tail_lines,
        limit_bytes,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> Tuple:

        _host = None

        _collection_formats: Dict[str, str] = {}

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[str, str] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if project_name is not None:

            _query_params.append(("project_name", project_name))

        if model_id is not None:

            _query_params.append(("model_id", model_id))

        if model_name is not None:

            _query_params.append(("model_name", model_name))

        if version_id is not None:

            _query_params.append(("version_id", version_id))

        if prediction_job_id is not None:

            _query_params.append(("prediction_job_id", prediction_job_id))

        if cluster is not None:

            _query_params.append(("cluster", cluster))

        if namespace is not None:

            _query_params.append(("namespace", namespace))

        if component_type is not None:

            _query_params.append(("component_type", component_type))

        if container_name is not None:

            _query_params.append(("container_name", container_name))

        if prefix is not None:

            _query_params.append(("prefix", prefix))

        if follow is not None:

            _query_params.append(("follow", follow))

        if previous is not None:

            _query_params.append(("previous", previous))

        if since_seconds is not None:

            _query_params.append(("since_seconds", since_seconds))

        if since_time is not None:

            _query_params.append(("since_time", since_time))

        if timestamps is not None:

            _query_params.append(("timestamps", timestamps))

        if tail_lines is not None:

            _query_params.append(("tail_lines", tail_lines))

        if limit_bytes is not None:

            _query_params.append(("limit_bytes", limit_bytes))

        # process the header parameters
        # process the form parameters
        # process the body parameter

        # authentication setting
        _auth_settings: List[str] = ["Bearer"]

        return self.api_client.param_serialize(
            method="GET",
            resource_path="/logs",
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth,
        )
