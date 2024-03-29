# Copyright 2020 The Merlin Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from models.validation import validate_model_dir
from models.model import ModelType
import pytest
import re


@pytest.mark.parametrize(
    "model_type,model_dir,message",
    [
        (
            ModelType.PYTORCH,
            "tests/models/invalid-models/pytorch-model-invalid",
            "tests/models/invalid-models/pytorch-model-invalid/config/config.properties is not found",
        ),
        (
            ModelType.TENSORFLOW,
            "tests/models/invalid-models/tensorflow-model-invalid",
            "tests/models/invalid-models/tensorflow-model-invalid/1/saved_model.pb is not found",
        ),
        (
            ModelType.SKLEARN,
            "tests/models/invalid-models/sklearn-model-invalid",
            "['model.joblib'] is not found in tests/models/invalid-models/sklearn-model-invalid",
        ),
        (
            ModelType.XGBOOST,
            "tests/models/invalid-models/xgboost-model-invalid",
            "['model.bst'] is not found in tests/models/invalid-models/xgboost-model-invalid",
        ),
        (
            ModelType.ONNX,
            "tests/models/invalid-models/onnx-model-invalid",
            "['model.onnx'] is not found in tests/models/invalid-models/onnx-model-invalid",
        ),
    ],
)
@pytest.mark.unit
def test_invalid_model_dir(model_type, model_dir, message):
    with pytest.raises(ValueError, match=re.escape(message)):
        validate_model_dir(model_type, model_dir)


@pytest.mark.parametrize(
    "model_type,model_dir",
    [
        (ModelType.PYTORCH, "tests/models/pytorch-model/pytorch-sample"),
        (ModelType.TENSORFLOW, "tests/models/tensorflow-model"),
        (ModelType.SKLEARN, "tests/models/sklearn-model"),
        (ModelType.XGBOOST, "tests/models/xgboost-model"),
        (ModelType.ONNX, "tests/models/onnx-model"),
    ],
)
@pytest.mark.unit
def test_valid_model_dir(model_type, model_dir):
    validate_model_dir(model_type, model_dir)
