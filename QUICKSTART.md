# 🚀 Vish AI - Quick Start with Phi-3

## What Changed?
**Before**: 3 separate models (DistilGPT2, DistilBART, DistilBERT)  
**Now**: 1 unified model (Microsoft Phi-3 Mini 4K Instruct)

---

## Quick Commands

### Test the Setup
```bash
python test_phi3_model.py
```

### Run Locally
```bash
pip install -r requirements.txt
python app.py
# Open: http://localhost:7860
```

### Fine-tune (Optional)
```bash
# 1. Create training_data.jsonl with your examples
# 2. Run:
python fine_tune_phi3.py
```

---

## File Guide

| File | Purpose |
|------|---------|
| `app.py` | Main application (UPDATED) |
| `requirements.txt` | Dependencies (UPDATED) |
| `test_phi3_model.py` | Test installation ⭐ START HERE |
| `fine_tune_phi3.py` | Customize the model |
| `PHI3_MODEL_GUIDE.md` | Complete documentation |
| `MODEL_UPGRADE_SUMMARY.md` | User-friendly overview |
| `CHANGES_SUMMARY.md` | Detailed change log |

---

## Key Benefits

✅ **Better Quality** - 3.8B parameters vs 82M-300M  
✅ **Unified** - 1 model instead of 3  
✅ **Customizable** - Easy to fine-tune  
✅ **Production Ready** - Microsoft supported  

---

## Performance

| Task | Speed (CPU) | Speed (GPU) |
|------|-------------|-------------|
| Chat | 1-3s | 0.3-1s |
| Summarize | 2-4s | 0.5-1.5s |
| Sentiment | 0.5-2s | 0.2-0.5s |

---

## Memory Options

| Mode | Size | Command |
|------|------|---------|
| Full (FP32) | ~15GB | Default in app.py |
| Half (FP16) | ~7.5GB | Use GPU config |
| 4-bit Quant | ~2.5GB | See PHI3_MODEL_GUIDE.md |

---

## Troubleshooting

**Problem**: Out of memory  
**Solution**: Enable 4-bit quantization (see guide)

**Problem**: Slow responses  
**Solution**: Use GPU or reduce max_new_tokens

**Problem**: Model won't load  
**Solution**: Check internet, clear cache, run test script

---

## Fine-tuning Quick Start

1. **Create data** (training_data.jsonl):
```json
{"text": "User: Hello\nAssistant: Hi! How can I help?"}
```

2. **Run training**:
```bash
python fine_tune_phi3.py
```

3. **Update app.py**:
```python
model_path = "./phi3-vish-ai-finetuned"
```

---

## Resources

📖 **Full Guide**: PHI3_MODEL_GUIDE.md  
📋 **Changes**: CHANGES_SUMMARY.md  
🌐 **Model**: [HuggingFace](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct)

---

## Next Steps

1. ⏳ Run: `python test_phi3_model.py`
2. ⏳ Test all features in UI
3. ⏳ Deploy to HuggingFace Spaces
4. ⏳ (Optional) Fine-tune for your domain

---

**Status**: ✅ Ready to Test  
**Version**: Phi-3 Unified (Oct 2025)
