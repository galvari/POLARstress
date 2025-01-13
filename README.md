# **POLARstress: Stress Detection Algorithm Using Polar Verity Sense HR Data**

## **About**
**POLARstress** is a lightweight, HR-based stress detection algorithm designed for **real-time continuous monitoring** using [**Polar Verity Sense**](https://www.polar.com) sensor data. It applies **Heart Rate Variability (HRV)** analysis to approximate stress levels using the **RMSSD (Root Mean Square of Successive Differences)** metric. The algorithm is optimized to work on **low computational power** devices, making it suitable for **real-time applications in clinical settings** such as **therapy sessions** and **biofeedback interventions**.

This project aims to detect **stress, arousal, stability, and relaxation** phases using only **HR (bpm)** signals, focusing on practical, deployable use in **mobile apps** or **wearable devices**.

---

### 🎯 **Key Features**
- **Stress Detection Using HR Only:** No need for complex PPG or ECG signals—works with simple HR data.
- **Baseline Calculation:** Automatic identification of the most relaxing 2-minute baseline period (if not provided).
- **Overlapping Windows Analysis:** Tracks RMSSD trends over time for continuous stress monitoring.
- **Stress Flagging:** Flags stress levels based on RMSSD thresholds (Stressed, Aroused, Stable, Relaxed).
- **Efficient Computation:** Designed to run on devices with limited processing power (e.g., wearables, mobile apps).

---

## **How It Works**
The algorithm performs the following steps:
1. **Data Processing:** Processes Polar Verity Sense session files and enriches them with timestamps.
2. **Outlier Removal & Interpolation:** Removes RR interval outliers and fills gaps in the data.
3. **Baseline Calculation:** Identifies a **baseline RMSSD** period by selecting the most relaxing 2-minute window.
4. **Overlapping Windows Analysis:** Computes **RMSSD values** for overlapping time windows to monitor HRV changes.
5. **Stress Flagging:** Flags each period as **High Stress**, **Moderate Stress**, **Normal**, or **Relaxed** based on deviations from the baseline.

---

## **Repository Structure**
```
POLARstress/
├── README.md
├── LICENSE.md
├── src/
│   ├── stress_detection_algo.py  # Main script for stress detection
├── data/
│   ├── sample_data1.csv      # Example Polar session data1
│   └── sample_data2.csv      # Example Polar session data1
└── requirements.txt
```

---

## **Script Details**

### **`stress_detection.py`**
The core script processes **Polar Verity Sense session files** to detect stress levels using **HR-based RMSSD calculations**. It performs:
- **Data Enrichment**
- **Outlier Removal**
- **Baseline RMSSD Calculation**
- **Overlapping Window RMSSD Calculation**
- **Stress Flagging**
- **Visualization (Optional)**

**Usage:**
```
python src/stress_detection.py --input_file <path/to/input.csv> --output_folder <path/to/output_folder> --save_plot
```
##### Sample data from session 1 and 2, output visualization:
![Flagging Visualization](/data/sample_data1.png "Sample data1 output visualization")
![Stress Visualization](/data/sample_data2.png "Sample data2 output visualization")
---

### Usage of Polar Verity Sense Sensor Data

This project processes HR (Heart Rate) data obtained from the Polar Verity Sense sensor. Please note:

The software is not affiliated with or endorsed by Polar Electro.

Users are responsible for ensuring compliance with the Polar terms of use and privacy policy when using Polar devices and data.

For more information on Polar products, visit: [https://www.polar.com](https://www.polar.com)


## **Requirements**

To install the required packages:
```
pip install -r requirements.txt
```

---

## **How Stress Levels Are Flagged**
Stress levels are determined by comparing the calculated **RMSSD values** with the baseline RMSSD. The system flags the stress levels as follows:

| **Stress Level**     | **Condition**                                 | **Color in Plot** |
|----------------------|-----------------------------------------------|-------------------|
| Stressed         | RMSSD ≤ baseline_mean - 2 * baseline_std      | Red            |
| Aroused      | baseline_mean - 2 * baseline_std < RMSSD ≤ baseline_mean - baseline_std | Yellow              |
|Stable    | baseline_mean - baseline_std < RMSSD ≤ baseline_mean + baseline_std | Green  |
| Relaxed              | RMSSD > baseline_mean + baseline_std          | Blue        |

---

## **License**
This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)**.

You are free to use, modify, and share the code for **non-commercial purposes** as long as proper attribution is given.

For any commercial use or inquiries, please contact the authors at **[your_email@example.com]**.

To view a copy of this license, visit:
[https://creativecommons.org/licenses/by-nc/4.0/](https://creativecommons.org/licenses/by-nc/4.0/)

---

## **References**

```bibtex
@article{alvari2024exploring,
  title={Exploring Physiological Responses in Virtual Reality-based Interventions for Autism Spectrum Disorder: A Data-Driven Investigation},
  author={Alvari, Gianpaolo and Vallefuoco, Ersilia and Cristofolini, Melanie and Salvadori, Elio and Dianti, Marco and Moltani, Alessia and Castello, Davide Dal and Venuti, Paola and Furlanello, Cesare},
  journal={arXiv preprint arXiv:2404.07159},
  year={2024}
}


@article{gabrielli2023co,
  title={Co-Design of a Virtual Reality Multiplayer Adventure Game for Adolescents With Autism Spectrum Disorder: Mixed Methods Study},
  author={Gabrielli, Silvia and Cristofolini, Melanie and Dianti, Marco and Alvari, Gianpaolo and Vallefuoco, Ersilia and Bentenuto, Arianna and Venuti, Paola and Ibarra, Oscar Mayora and Salvadori, Elio and others},
  journal={JMIR Serious Games},
  volume={11},
  number={1},
  pages={e51719},
  year={2023},
  publisher={JMIR Publications Inc., Toronto, Canada}
}
```
