# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""A sample plugin to demonstrate reading scalars."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import csv
import functools
import json
import mimetypes
import os

import six
from werkzeug import wrappers
import werkzeug

from tensorboard import errors
from tensorboard import plugin_util
from tensorboard.backend import http_util
from tensorboard.plugins import base_plugin
from tensorboard.util import tensor_util
from tensorboard.plugins.scalar import metadata

_SCALAR_PLUGIN_NAME = metadata.PLUGIN_NAME
_PLUGIN_DIRECTORY_PATH_PART = "/data/plugin/my_new_plugin/"


class ExampleRawScalarsPlugin(base_plugin.TBPlugin):
    """Raw summary example plugin for TensorBoard."""

    plugin_name = "my_new_plugin"

    def __init__(self, context):
        """Instantiates ExampleRawScalarsPlugin.

        Args:
          context: A base_plugin.TBContext instance.
        """
        self._multiplexer = context.multiplexer

    def get_plugin_apps(self):
        return {
            "/scalars": self.scalars_route,
            "/tags": self._serve_tags,
            "/models": self._serve_models,
            "/datasets": self.serve_datasets,
            "/data_indices": self.serve_data_indices,
            "/data": self.serve_data,
            "/static/*": self._serve_static_file,
        }

    @wrappers.Request.application
    def _serve_tags(self, request):
        """Serves run to tag info.

        Frontend clients can use the Multiplexer's run+tag structure to request data
        for a specific run+tag. Responds with a map of the form:
        {runName: [tagName, tagName, ...]}
        """
        run_tag_mapping = self._multiplexer.PluginRunToTagToContent(
            _SCALAR_PLUGIN_NAME
        )
        run_info = {
            run: list(tags) for (run, tags) in six.iteritems(run_tag_mapping)
        }
        return http_util.Respond(request, run_info, "application/json")

    @wrappers.Request.application
    def _serve_models(self, request):
        runs = self._multiplexer.Runs()
        run_names = {run: run for run in runs.keys()}
        return http_util.Respond(request, run_names, "application/json")

    @wrappers.Request.application
    def serve_datasets(self, request):
        """Serves example to indices info.

        Frontend clients can use the Multiplexer's index to request data
        for a specific example. Responds with a map of the form:
        {"nl": Str, "nl_type": str, "schema": image}
        """
        # Load datasets
        model = request.args.get("model")
        datasets = {}
        try:
            for idx, item in enumerate(self._multiplexer.Tensors(model, "datasets")):
                dataset = item.tensor_proto.string_val[0].decode("utf-8")
                datasets[dataset] = dataset
        except:
            print("No datasets for model: {}".format(model))

        return http_util.Respond(request, datasets, "application/json")

    @wrappers.Request.application
    def serve_data_indices(self, request):
        model = request.args.get("model")
        dataset = request.args.get("dataset")
        data_indices = {}
        try:
            # get total number of steps for model and dataset
            num = len(self._multiplexer.Tensors(model, "{}_query".format(dataset)))
            data_indices = {str(idx): str(idx) for idx in range(num)}
        except:
            print("no data for model:{} dataset:{}",format(model, dataset))

        print("{} {}".format(model, dataset))
        print(data_indices)
        return http_util.Respond(request, data_indices, "application/json")


    @wrappers.Request.application
    def _serve_static_file(self, request):
        """Returns a resource file from the static asset directory.

        Requests from the frontend have a path in this form:
        /data/plugin/example_raw_scalars/static/foo
        This serves the appropriate asset: ./static/foo.

        Checks the normpath to guard against path traversal attacks.
        """
        static_path_part = request.path[len(_PLUGIN_DIRECTORY_PATH_PART) :]
        resource_name = os.path.normpath(
            os.path.join(*static_path_part.split("/"))
        )
        if not resource_name.startswith("static" + os.path.sep):
            return http_util.Respond(
                request, "Not found", "text/plain", code=404
            )

        resource_path = os.path.join(os.path.dirname(__file__), resource_name)
        with open(resource_path, "rb") as read_file:
            mimetype = mimetypes.guess_type(resource_path)[0]
            return http_util.Respond(
                request, read_file.read(), content_type=mimetype
            )

    @wrappers.Request.application
    def serve_data(self, request):
        model = request.args.get("model")
        dataset = request.args.get("dataset")
        data_idx = request.args.get("index")
        query = self.get_data(model, dataset, "query", data_idx)
        query_type = self.get_data(model, dataset, "query_type", data_idx)
        db = self.get_data(model, dataset, "db", data_idx)
        schema = self.get_data(model, dataset, "schema", data_idx)
        gold = self.get_data(model, dataset, "gold", data_idx)
        pred = self.get_data(model, dataset, "pred", data_idx)

        body = {
            "query": query,
            "queryType": query_type,
            "db": db,
            "schema": schema,
            "gold": gold,
            "pred": pred,
        }

        return http_util.Respond(request, body, "application/json")

    def is_active(self):
        """Returns whether there is relevant data for the plugin to process.

        When there are no runs with scalar data, TensorBoard will hide the plugin
        from the main navigation bar.
        """
        return bool(
            self._multiplexer.PluginRunToTagToContent(_SCALAR_PLUGIN_NAME)
        )

    def frontend_metadata(self):
        return base_plugin.FrontendMetadata(es_module_path="/static/index.js")

    def get_data(self, model, dataset, tag, data_idx):
        try:
            tensor_event = self._multiplexer.Tensors(model, "{}_{}".format(dataset, tag))[int(data_idx)]
            value = tensor_event.tensor_proto.string_val[0].decode("utf-8")
        except KeyError:
            raise errors.NotFoundError("No data found")
        return value

    def get_dataset_path(self, run, dataset):
        try:
            tensor_event = self._multiplexer.Tensors(run, "{}_path".format(dataset))[0]
            value = tensor_event.tensor_proto.string_val[0].decode("utf-8")
        except KeyError:
            raise errors.NotFoundError("No dataset recorded")
        return value

    @wrappers.Request.application
    def scalars_route(self, request):
        run = request.args.get("run")
        return http_util.Respond(request, [], "application/json")
