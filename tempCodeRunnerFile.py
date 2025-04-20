    # Save SVG version
    nat_svg_path = os.path.join(new_folder, "natural_lang.svg")
    fig.savefig(nat_svg_path)
    print(f"natural_lang.svg saved to {nat_svg_path}")

    # =========== wave_comparison => original vs modified =============
    for line in ax.lines[:]:
        line.remove()

    if ep.final_line is not None:
        ep.final_line.remove()
        ep.final_line = None

    print("\n=== wave_comparison Color Picker ===")
    c_bg, c_pos, c_neg = run_color_picker("#000000", "#00FF00", "#FF0000")
    ep.reapply_colors(c_bg, c_pos, c_neg)
    ep.comparison_line_orig, = ax.plot(ep.audio_data, lw=2, label='Original Wave')
    ep.comparison_line_mod,  = ax.plot(mod_wave, lw=2, label='Modified Wave')
    ep.reapply_colors(c_bg, c_pos, c_neg, final_wave_color=c_pos)
    ax.legend(loc='upper right').get_frame().set_alpha(0.5)
    ax.set_xlim(0, ep.num_points)
    ax.set_ylim(-L, L)
    ax.set_aspect('auto')
    cmp_path = os.path.join(new_folder, "wave_comparison.png")
    fig.savefig(cmp_path)
    print(f"wave_comparison.png saved to {cmp_path}")
    # Save SVG version
    cmp_svg_path = os.path.join(new_folder, "wave_comparison.svg")
    fig.savefig(cmp_svg_path)
    print(f"wave_comparison.svg saved to {cmp_svg_path}")
    plt.close()

def main():
    while True:
        process_single_file()
        cont = input("\nDo you want to process another file? (y/n): ").strip().lower()
        if cont != 'y':
            print("Exiting program.")
            break

if __name__ == '__main__':
    main()
