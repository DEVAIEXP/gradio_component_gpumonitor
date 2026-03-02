# `gradio-gpu-monitor`
<img alt="Static Badge" src="https://img.shields.io/badge/version%20-%200.0.1%20-%20blue">  
<a href="https://huggingface.co/spaces/elismasilva/gradio_gpu_monitor"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Demo-blue"></a>  
<span>💻 <a href='https://github.com/DEVAIEXP/gradio_component_gpumonitor'>Component GitHub Code</a></span>

Custom real-time GPU monitoring component for Gradio apps using `gr.HTML`. It polls `nvidia-smi` in the background and displays live statistics (VRAM, Temperature, Load, Power, and Clocks) in an elegant, responsive grid.

Perfect for AI training dashboards, LLM hosting interfaces, or any Gradio app where users need to keep an eye on hardware resource consumption.

Inspired by the GPU monitoring widget from the Ostris [AI-Toolkit](https://github.com/ostris/ai-toolkit)

## Features and Key Characteristics

- **Real-time targeted updates** with zero DOM flickering or flashing.
- **Autonomous background polling** using Gradio 6's `server_functions`.
- **Light/dark theme support** completely integrated with Gradio's native `--` CSS variables.
- **Graceful fallback (Mock Data)** if executed on a machine without `nvidia-smi` (ideal for local development).
- **Responsive CSS Grid** that automatically adapts the number of columns based on screen size.
- **Dynamic colored icons** via Lucide (temperature and utilization colors change based on thresholds).
- **Configurable** refresh rate and timestamp visibility.

## Installation

```bash
pip install gradio-gpu-monitor
```

## Usage
*Note: Make sure to include the Lucide icon library in your `gr.launch()` head parameter for the icons to render correctly.*

```py
import gradio as gr
from gradio_gpu_monitor import GPUMonitor

# Load Lucide icons via CDN
head_html = """<script src="https://unpkg.com/lucide@latest"></script>"""

with gr.Blocks(head=head_html) as demo:
    gr.Markdown("# 🎛️ System Dashboard")
    
    # Simple initialization with default settings (1s refresh)
    GPUMonitor()
    
demo.launch()
```
Check out the full example in the [Hugging Face demo.](https://huggingface.co/spaces/elismasilva/gradio_gpu_monitor)

| Property | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `update_interval` | `int` | `1000` | Polling interval in milliseconds (how often the GPU data refreshes). |
| `show_last_updated` | `bool` | `True` | Whether to display the "Last updated: HH:MM:SS" text in the header. |
| `label` | `str \| None` | `None` | Optional label for the component. |
| `visible` | `bool` | `True` | Whether the component is visible on the screen. |
| `elem_id` | `str \| None` | `None` | Custom HTML ID for targeting with CSS or JavaScript. |
| `elem_classes` | `list[str] \| str \| None` | `None` | Additional CSS classes applied to the component wrapper. |

### Example with all properties

```py
gpu_widget = GPUMonitor(
    update_interval=2500,              # Refresh every 2.5 seconds
    show_last_updated=False,           # Hide the clock text
    label="Hardware Status",           # Optional title context
    visible=True,
    elem_id="custom-gpu-monitor",
    elem_classes=["my-custom-class"]
)
```

