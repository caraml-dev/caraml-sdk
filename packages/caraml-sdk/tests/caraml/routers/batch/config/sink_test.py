import pytest
import caraml.routers.batch.config.sink
import caraml.routers.client.models


@pytest.mark.parametrize(
    "table,staging_bucket,options,save_mode,columns,expected",
    [
        pytest.param(
            "project.dataset.results_table",
            "my-staging_bucket",
            {"partitionField": "target_date"},
            caraml.routers.batch.config.sink.SaveMode.APPEND,
            ["target_date", "user_id", "prediction_score"],
            caraml.routers.client.models.BigQuerySink(
                save_mode=caraml.routers.client.models.SaveMode("APPEND"),
                columns=["target_date", "user_id", "prediction_score"],
                bq_config=caraml.routers.client.models.BigQuerySinkConfig(
                    table="project.dataset.results_table",
                    staging_bucket="my-staging_bucket",
                    options={"partitionField": "target_date"},
                ),
            ),
            id="Initialize BQ sink",
        )
    ],
)
def test_create_bq_sink(table, staging_bucket, options, save_mode, columns, expected):
    sink = (
        caraml.routers.batch.config.sink.BigQuerySink(table, staging_bucket, options)
        .select(columns)
        .save_mode(save_mode)
    )

    assert sink.to_open_api() == expected
