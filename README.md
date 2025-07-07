# NameSmithy 🔨

**GAN-Based Baby Name Generator & Evaluator**

Generate unique baby names that look historically popular using adversarial machine learning trained on 140+ years of US naming data.

<div align="center">

## 🚀 **Try NameSmithy Now!**

### 🌐 [**Interactive Google Colab Demo →**](https://colab.research.google.com/github/michaelmw/NameSmithy/blob/main/NameSmithy_Colab_Demo.ipynb)
*Full AI functionality - click and run in your browser!*

### 📱 [**Frontend Preview →**](https://michaelmw.github.io/NameSmithy)  
*Interface preview (GitHub Pages demo mode)*

</div>

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ✨ Key Innovation

**Generate "Popular-Looking" Unique Names**: Our GAN framework learned linguistic features from 77K+ historical names, enabling generation of completely new names that have never existed but carry the ML characteristics of popular names.

## 🧠 How It Works

1. **Training Data**: 140+ years of US baby names (1880-2018) curated from Social Security records
2. **Scoring System**: Higher scores = historically more popular; bad words assigned negative scores  
3. **GAN Framework**: Neural network learns language patterns in adversarial setup
4. **Dual Output**: Both generator (creates names) and evaluator (scores quality) from same training

## 🎯 Features

- **Unique Name Generation**: Create names never seen in historical data that "look" popular
- **Quality Control**: Score range filtering (0-100 scale)
- **Style Options**: Random, Popular (database names), Unique (new names only)
- **Real-time Generation**: Live progress with abort capability
- **Instant Evaluation**: Score any name with historical context

## 🚀 Quick Start Options

### Option 1: Google Colab (Recommended)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/michaelmw/NameSmithy/blob/main/NameSmithy_Colab_Demo.ipynb)

**Zero setup required!** Just click the badge above and run all cells.
- ✅ Full AI functionality in your browser
- ✅ No installation or configuration needed  
- ✅ Free GPU access from Google
- ✅ Share results via public URL

### Option 2: Local Development
```bash
git clone https://github.com/michaelmw/NameSmithy.git
cd NameSmithy
pip install -r requirements.txt
python server.py
# Open browser to http://localhost:5001
```

*Completely standalone - all models included (27MB)*

## 🏗️ GAN Architecture

**Generator**: Character-level neural network creates phonetically valid names  
**Discriminator**: Gradient boosting model evaluates name "popularity" based on learned features  
**Training**: Adversarial learning on 77K+ name-popularity pairs + curated bad words

## 📖 Usage

**Generator**: Select gender → Choose style (Random/Popular/Unique) → Set quality range → Generate  
**Evaluator**: Enter name → Get instant score and historical ranking

**Key Use Case**: Select "Unique" style to generate names that never existed but have learned features of popular names.

### API
```bash
POST /api/generate {"style": "unique", "min_score": 70}
POST /api/evaluate {"name": "Isabella", "gender": "F"}
```

## 🎯 Performance

**Training**: 77K+ name-popularity pairs + 1K+ bad words with negative scores  
**Quality**: Deterministic scoring, same input = same output  
**Innovation**: Generate novel names with popular name characteristics

## 🛠️ Repository Structure

```
NameSmithy/
├── server.py                      # Flask server with GAN models
├── NameSmithy_Colab_Demo.ipynb    # 🌟 Google Colab interactive demo
├── requirements.txt               # Python dependencies
├── models/                        # ML models and training data
├── docs/                          # Web interface files
├── README.md                      # This documentation
└── LICENSE                        # MIT License
```

**Tech**: Python + Flask + NumPy + scikit-learn | JavaScript + HTML5 + CSS3

## 🔬 Technical Details

**Session Architecture**: Concurrent users, real-time progress, abort-safe  
**Randomization**: High-entropy seeding prevents repeated patterns  
**GAN Training**: Adversarial framework learns linguistic features from historical popularity data

---

<div align="center">

### 🚀 [**Interactive Colab Demo**](https://colab.research.google.com/github/michaelmw/NameSmithy/blob/main/NameSmithy_Colab_Demo.ipynb) | [**GitHub Repository**](https://github.com/michaelmw/NameSmithy)

*NameSmithy: Generate unique names that look popular using GAN-learned linguistic features*

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/michaelmw/NameSmithy/blob/main/NameSmithy_Colab_Demo.ipynb)

**MIT Licensed** • Built with ❤️ for parents and name enthusiasts

</div>