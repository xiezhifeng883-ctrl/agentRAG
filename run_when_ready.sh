#!/bin/bash
# Auto-run comprehensive tests once sentence-transformers is installed

echo "=========================================="
echo "Waiting for sentence-transformers installation..."
echo "=========================================="

# Wait for installation to complete
while true; do
    if python -c "import sentence_transformers" 2>/dev/null; then
        echo "✅ sentence-transformers installed!"
        break
    else
        echo "⏳ Still installing... (checking every 30s)"
        sleep 30
    fi
done

# Show installed version
echo ""
echo "Installed versions:"
python -c "
import sentence_transformers
import faiss
import numpy as np
print(f'  sentence-transformers: {sentence_transformers.__version__}')
print(f'  faiss: {faiss.__version__}')
print(f'  numpy: {np.__version__}')
"

# Run comprehensive tests
echo ""
echo "=========================================="
echo "Running comprehensive tests..."
echo "=========================================="

cd /home/user/agentRAG
python test_comprehensive.py

# Show results
echo ""
echo "=========================================="
echo "Test execution complete!"
echo "=========================================="
echo ""
echo "To run tests manually:"
echo "  python test_comprehensive.py"
echo "  python demo_without_api.py"
echo ""
echo "To use the RAG system:"
echo "  export ANTHROPIC_API_KEY='your-key'"
echo "  python cli.py add --files document.pdf --store-name my_docs"
echo "  python cli.py query --interactive --store-name my_docs"
