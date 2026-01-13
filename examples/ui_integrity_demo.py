"""
Example: Using Chrome DevTools Extension for Visual QA
Demonstrates accessibility checking, contrast validation, and visual regression testing.
"""

from confucius_agent.orchestrator import Orchestrator
from confucius_agent.ui_integrity import ChromeDevToolsExtension
from confucius_agent.memory import MemoryManager


def example_1_basic_visual_qa():
    """Example 1: Basic visual QA workflow"""
    print("\n" + "="*70)
    print("Example 1: Basic Visual QA Workflow")
    print("="*70)
    
    # Initialize agent with Chrome DevTools
    agent = Orchestrator()
    chrome_ext = ChromeDevToolsExtension(
        chrome_port=9222,
        auto_start_chrome=True
    )
    agent.add_extension(chrome_ext)
    
    # Visual QA workflow
    workflow = """
    Visual QA for localhost:5173 dashboard:
    
    1. Navigate to http://localhost:5173
    2. Wait for page load (network idle)
    3. Capture full-page screenshot
    4. Check contrast ratios for:
       - Body text
       - Headings (h1, h2, h3)
       - Links (normal, hover, visited)
       - Buttons (primary, secondary)
       - Error messages
    5. Report WCAG compliance (AA and AAA levels)
    6. If any failures, suggest specific color adjustments
    """
    
    result = agent.run(workflow)
    
    print(f"\nVisual QA complete. Check artifacts for screenshots and reports.")
    print(f"Total steps: {len(result.context.actions)}")


def example_2_contrast_ratio_checking():
    """Example 2: Detailed contrast ratio analysis"""
    print("\n" + "="*70)
    print("Example 2: WCAG Contrast Ratio Analysis")
    print("="*70)
    
    chrome_ext = ChromeDevToolsExtension()
    
    # Test various color combinations
    test_cases = [
        # (fg_rgb, bg_rgb, label)
        ((255, 255, 255), (30, 30, 30), "White on dark gray"),
        ((0, 0, 0), (255, 255, 255), "Black on white"),
        ((100, 100, 100), (255, 255, 255), "Gray on white"),
        ((255, 87, 51), (255, 255, 255), "Orange on white"),
    ]
    
    print("\nContrast Ratio Analysis:")
    print("-" * 70)
    
    for fg, bg, label in test_cases:
        ratio = chrome_ext.calculate_contrast_ratio(fg, bg)
        compliance = chrome_ext.check_wcag_compliance(ratio, font_size=16, font_weight=400)
        
        print(f"\n{label}")
        print(f"  FG: rgb{fg}")
        print(f"  BG: rgb{bg}")
        print(f"  Contrast: {ratio:.2f}:1")
        print(f"  WCAG AA: {'✓ Pass' if compliance['AA'] else '✗ Fail'}")
        print(f"  WCAG AAA: {'✓ Pass' if compliance['AAA'] else '✗ Fail'}")
        
        # Suggest improvements if needed
        if not compliance['AA']:
            suggestions = chrome_ext.suggest_color_adjustment(fg, bg, target_ratio=4.5)
            if suggestions['suggestions']:
                print(f"  💡 Suggested fix: {suggestions['suggestions'][0]['type']}")
                print(f"     New color: {suggestions['suggestions'][0]['color']}")
                print(f"     New ratio: {suggestions['suggestions'][0]['ratio']:.2f}:1")


def example_3_dark_mode_validation():
    """Example 3: Dark mode color palette validation"""
    print("\n" + "="*70)
    print("Example 3: Dark Mode Palette Validation")
    print("="*70)
    
    # Define dark mode palette
    dark_palette = {
        "background": (24, 24, 27),      # zinc-900
        "text": (250, 250, 250),         # zinc-50
        "text_muted": (161, 161, 170),   # zinc-400
        "primary": (59, 130, 246),       # blue-500
        "success": (34, 197, 94),        # green-500
        "error": (239, 68, 68),          # red-500
        "border": (63, 63, 70)           # zinc-700
    }
    
    chrome_ext = ChromeDevToolsExtension()
    
    print("\nDark Mode Palette:")
    print(f"Background: rgb{dark_palette['background']}")
    print("\nWCAG Compliance Check:")
    print("-" * 70)
    
    # Check all text colors against background
    text_elements = [
        ("Primary Text", dark_palette['text'], 16, 400),
        ("Muted Text", dark_palette['text_muted'], 14, 400),
        ("Primary Button", dark_palette['primary'], 16, 600),
        ("Success Message", dark_palette['success'], 14, 400),
        ("Error Message", dark_palette['error'], 14, 400),
    ]
    
    all_pass = True
    
    for label, fg_color, font_size, font_weight in text_elements:
        ratio = chrome_ext.calculate_contrast_ratio(fg_color, dark_palette['background'])
        compliance = chrome_ext.check_wcag_compliance(ratio, font_size, font_weight)
        
        status = "✓" if compliance['AA'] else "✗"
        print(f"{status} {label:20} {ratio:5.2f}:1  ", end="")
        print(f"AA: {'Pass' if compliance['AA'] else 'FAIL'} | ", end="")
        print(f"AAA: {'Pass' if compliance['AAA'] else 'Fail'}")
        
        if not compliance['AA']:
            all_pass = False
            suggestions = chrome_ext.suggest_color_adjustment(
                fg_color, 
                dark_palette['background'], 
                target_ratio=4.5
            )
            print(f"  💡 Needs adjustment: {suggestions}")
    
    print("-" * 70)
    print(f"\n{'✓ All colors pass WCAG AA' if all_pass else '✗ Some colors need adjustment'}")


def example_4_ralph_loop_visual_testing():
    """Example 4: Autonomous visual regression testing with Ralph loops"""
    print("\n" + "="*70)
    print("Example 4: Ralph Loop Visual Regression Testing")
    print("="*70)
    
    # Initialize agent with memory and Chrome
    memory = MemoryManager()
    agent = Orchestrator()
    chrome_ext = ChromeDevToolsExtension(auto_start_chrome=True)
    agent.add_extension(chrome_ext)
    
    # Ralph loop for continuous visual testing
    ralph_workflow = """
    Ralph Loop: Continuous Visual Regression Testing
    
    Initial Setup:
    1. Navigate to test environment (localhost:5173)
    2. Capture baseline screenshots for all key pages
    3. Run accessibility audit and store results
    
    Loop (repeat every code change):
    1. Wait for file system changes or manual trigger
    2. Navigate to each key page
    3. Capture current screenshots
    4. Compare with baseline (pixel diff)
    5. Re-run accessibility audit
    6. If differences detected:
       a. Generate visual diff report
       b. Check if contrast ratios changed
       c. Alert if WCAG compliance degraded
       d. Store results in memory
    7. Update baseline if changes approved
    8. Export memory state for history tracking
    
    Success Criteria:
    - No WCAG AA failures introduced
    - Visual changes intentional and approved
    - Contrast ratios maintained or improved
    
    Exit Conditions:
    - Manual stop signal
    - Critical accessibility failure (auto-revert)
    """
    
    print("\nRalph Loop Configuration:")
    print("  • Continuous visual monitoring")
    print("  • Automatic accessibility checks")
    print("  • Baseline comparison with pixel diffing")
    print("  • Memory-backed test history")
    
    print("\nTo run this loop:")
    print("  result = agent.run(ralph_workflow)")
    print("  # Loop executes autonomously until exit condition")


def example_5_multi_viewport_testing():
    """Example 5: Test across multiple viewport sizes"""
    print("\n" + "="*70)
    print("Example 5: Multi-Viewport Responsive Testing")
    print("="*70)
    
    viewports = [
        ("Mobile", 375, 667),
        ("Tablet", 768, 1024),
        ("Desktop", 1920, 1080),
    ]
    
    agent = Orchestrator()
    chrome_ext = ChromeDevToolsExtension(auto_start_chrome=True)
    agent.add_extension(chrome_ext)
    
    print("\nTesting viewports:")
    for name, width, height in viewports:
        print(f"  • {name}: {width}x{height}")
    
    workflow = """
    Multi-viewport visual QA:
    
    For each viewport (Mobile, Tablet, Desktop):
    1. Set viewport size
    2. Navigate to target URL
    3. Wait for responsive layout
    4. Capture screenshot
    5. Check text legibility (min 16px body, 14px small)
    6. Check touch target sizes (min 44x44px on mobile)
    7. Verify contrast ratios
    8. Test keyboard navigation
    
    Generate responsive compliance report
    """
    
    print("\nWorkflow ready. Execute with:")
    print("  result = agent.run(workflow)")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("Chrome DevTools Extension - Visual QA Examples")
    print("="*70)
    print("\nThese examples demonstrate:")
    print("  1. Basic visual QA workflow")
    print("  2. WCAG contrast ratio analysis")
    print("  3. Dark mode palette validation")
    print("  4. Ralph loop autonomous testing")
    print("  5. Multi-viewport responsive testing")
    
    # Run non-agent examples (don't require Chrome running)
    example_2_contrast_ratio_checking()
    example_3_dark_mode_validation()
    
    print("\n" + "="*70)
    print("To run agent-based examples (1, 4, 5):")
    print("  1. Start Chrome: python scripts/launch_chrome.py start")
    print("  2. Uncomment examples in main()")
    print("  3. python examples/ui_integrity_demo.py")
    print("="*70 + "\n")
    
    # Uncomment to run agent-based examples:
    # example_1_basic_visual_qa()
    # example_4_ralph_loop_visual_testing()
    # example_5_multi_viewport_testing()


if __name__ == "__main__":
    main()
