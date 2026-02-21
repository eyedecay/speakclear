from __future__ import annotations


def plot_wpm_sections(sections: list[dict]) -> None:
    """
    Plots a bar chart of speaking speed (WPM) per 50-word section.
    Args:
        sections (list[dict]): List of section dicts from get_section_analysis.
    Returns:
        (None): Displays the plot window.
    """
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    if not sections:
        print("No sections to plot.")
        return

    section_labels = [f"S{s['section_index']}\n(w{s['word_start']}-{s['word_end']})" for s in sections]
    wpms = [s['wpm'] for s in sections]
    colors = ['#2ecc71' if s['understanding'] == 'high' else '#e74c3c' for s in sections]

    fig, ax = plt.subplots(figsize=(max(6, len(sections) * 1.2), 5))
    bars = ax.bar(section_labels, wpms, color=colors, edgecolor='white', linewidth=0.8)

    ax.axhline(y=120, color='gray', linestyle='--', linewidth=0.8)
    ax.axhline(y=160, color='steelblue', linestyle='--', linewidth=0.8)

    for bar, wpm in zip(bars, wpms):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.5,
            str(wpm),
            ha='center', va='bottom', fontsize=9, fontweight='bold'
        )

    high_patch = mpatches.Patch(color='#2ecc71', label='High understanding')
    low_patch = mpatches.Patch(color='#e74c3c', label='Low understanding')
    slow_line = plt.Line2D([0], [0], color='gray', linestyle='--', linewidth=0.8, label='Slow (120 WPM)')
    fast_line = plt.Line2D([0], [0], color='steelblue', linestyle='--', linewidth=0.8, label='Fast (160 WPM)')
    ax.legend(handles=[high_patch, low_patch, slow_line, fast_line], loc='upper right')

    ax.set_xlabel('Section (word range)')
    ax.set_ylabel('Words Per Minute (WPM)')
    ax.set_title('Speaking Speed per 50-Word Section')
    ax.set_ylim(0, max(wpms) * 1.2)
    plt.tight_layout()
    plt.show()