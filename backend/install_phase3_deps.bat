@echo off
echo Installing Phase 3 Dependencies for Enhanced Features...
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Installing search and vector database libraries...
pip install opensearch-py==2.4.0
pip install qdrant-client==1.7.0
echo.
echo Installing NLP and healthcare libraries...
pip install scispacy==0.5.3
echo.
echo Installing medical spaCy model...
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_core_sci_md-0.5.3-py3-none-any.whl
echo.
echo Installing updated requirements...
pip install -r requirements.txt
echo.
echo Phase 3 dependencies installation completed!
echo.
echo Testing enhanced imports...
python -c "from opensearchpy import OpenSearch; print('✅ OpenSearch available')"
python -c "from qdrant_client import QdrantClient; print('✅ Qdrant available')"
python -c "import scispacy; print('✅ scispaCy available')"
echo.
echo Press any key to exit...
pause > nul
