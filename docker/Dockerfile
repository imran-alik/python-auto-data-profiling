FROM python:3.12-slim

ARG ONPREM_DATA_PATH=/data/inbound
ARG REPORT_OUTPUT=/app/visualizations

ENV ONPREM_DATA_PATH=${ONPREM_DATA_PATH}
ENV REPORT_OUTPUT=${REPORT_OUTPUT}
ENV PYTHONPATH=/app/codebase:/app/packages

WORKDIR /app

COPY pyproject.toml README.md COMPLIANCE.md ./
COPY packages/ packages/
COPY codebase/ codebase/
COPY medallion/ medallion/
COPY data/source/samples/ data/source/samples/

RUN pip install --no-cache-dir -e .

RUN mkdir -p ${REPORT_OUTPUT} data/evidence medallion/output

CMD ["python", "-c", "from auto_profiler.orchestration.run_profile import run_profile; from auto_profiler.config.settings import ProfilerConfig; import os; c=ProfilerConfig(source_csv=os.environ.get('ONPREM_DATA_PATH', 'data/source/samples/telco_features_sample.csv'), report_output_dir=os.environ.get('REPORT_OUTPUT', 'visualizations')); print(run_profile(c))"]
