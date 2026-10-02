import streamlit as st
from utils.styling import clean_html

def hero_section(title: str, subtitle: str, badge_text: str = None):
    """Renders a premium Vercel-like hero section with gradient headings."""
    badge_html = ""
    if badge_text:
        badge_html = f"""
        <div style='display: inline-flex; align-items: center; background: rgba(99, 102, 241, 0.1); 
                    border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 9999px; 
                    padding: 4px 12px; margin-bottom: 1.5rem;' class='animate-fade-in'>
            <span style='font-size: 0.75rem; font-weight: 600; color: #a5b4fc; text-transform: uppercase; letter-spacing: 0.05em;'>
                ✨ {badge_text}
            </span>
        </div>
        """
        
    html = f"""
    <div style='text-align: center; padding: 4rem 1rem 3rem 1rem;' class='animate-fade-in'>
        {badge_html}
        <h1 style='font-size: 3.5rem; font-weight: 800; line-height: 1.1; margin-bottom: 1.5rem; letter-spacing: -0.025em;'>
            <span class='gradient-text'>{title}</span>
        </h1>
        <p style='font-size: 1.25rem; color: #a1a1aa; max-width: 42rem; margin: 0 auto 2.5rem auto; line-height: 1.6;'>
            {subtitle}
        </p>
    </div>
    """
    st.markdown(clean_html(html), unsafe_allow_html=True)

def section_header(title: str, subtitle: str = None, icon: str = ""):
    """Renders a structured, clean section header."""
    icon_html = f"<span style='margin-right: 0.5rem;'>{icon}</span>" if icon else ""
    subtitle_html = f"<p style='color: #a1a1aa; margin-top: 0.25rem; font-size: 0.95rem;'>{subtitle}</p>" if subtitle else ""
    
    html = f"""
    <div style='margin-top: 1.5rem; margin-bottom: 2rem;' class='animate-fade-in'>
        <h2 style='font-size: 1.75rem; font-weight: 700; color: #ffffff; display: flex; align-items: center;'>
            {icon_html}{title}
        </h2>
        {subtitle_html}
    </div>
    """
    st.markdown(clean_html(html), unsafe_allow_html=True)

def metric_card(title: str, value: str, change: str = None, is_positive: bool = True, icon: str = "📊"):
    """Renders a native Streamlit metric styled as a card."""
    label = f"{icon} {title}"
    delta = change
    delta_color = "normal" if is_positive else "inverse"
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)

def feature_card(title: str, description: str, icon: str = "⚡"):
    """Renders a landing page feature block card."""
    html = f"""
    <div class='glass-card glow-border' style='height: 100%;'>
        <div style='background: rgba(99, 102, 241, 0.1); border-radius: 12px; width: 44px; height: 44px; 
                    display: flex; align-items: center; justify-content: center; margin-bottom: 1.25rem;
                    border: 1px solid rgba(99, 102, 241, 0.2); font-size: 1.3rem;'>
            {icon}
        </div>
        <h3 style='font-size: 1.2rem; font-weight: 600; color: #ffffff; margin-bottom: 0.5rem;'>{title}</h3>
        <p style='color: #a1a1aa; font-size: 0.9rem; line-height: 1.5;'>{description}</p>
    </div>
    """
    st.markdown(clean_html(html), unsafe_allow_html=True)

def status_badge(status_type: str, label: str):
    """
    Returns HTML string of a styled pill status badge.
    Types: 'success', 'warning', 'danger', 'info'
    """
    colors = {
        "success": ("rgba(16, 185, 129, 0.1)", "rgba(16, 185, 129, 0.3)", "#34d399"),
        "warning": ("rgba(245, 158, 11, 0.1)", "rgba(245, 158, 11, 0.3)", "#fbbf24"),
        "danger": ("rgba(239, 68, 68, 0.1)", "rgba(239, 68, 68, 0.3)", "#f87171"),
        "info": ("rgba(99, 102, 241, 0.1)", "rgba(99, 102, 241, 0.3)", "#818cf8"),
    }
    bg, border, text = colors.get(status_type, colors["info"])
    
    return f"""
    <span style='display: inline-flex; align-items: center; background: {bg}; border: 1px solid {border}; 
                 color: {text}; font-size: 0.75rem; font-weight: 600; border-radius: 9999px; padding: 2px 8px;'>
        {label}
    </span>
    """

def footer():
    """Renders a Notion/Stripe-styled global footer."""
    html = """
    <div class='footer-text'>
        <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1.5rem; max-width: 1200px; margin: 0 auto;'>
            <div style='display: flex; align-items: center; gap: 0.5rem;'>
                <span class='footer-logo brand-gradient'>CleanAI</span>
                <span style='color: #3f3f46;'>|</span>
                <span>Intelligent Data Quality Platform</span>
            </div>
            <div style='display: flex; gap: 1.5rem;'>
                <a href='#' style='color: #71717a; text-decoration: none;'>Documentation</a>
                <a href='#' style='color: #71717a; text-decoration: none;'>Terms</a>
                <a href='#' style='color: #71717a; text-decoration: none;'>Privacy</a>
                <a href='#' style='color: #71717a; text-decoration: none;'>Support</a>
            </div>
        </div>
        <div style='margin-top: 1.5rem; font-size: 0.8rem; color: #52525b;'>
            &copy; 2026 CleanAI. Data quality workflows powered by Streamlit and configured AI providers.
        </div>
    </div>
    """
    st.markdown(clean_html(html), unsafe_allow_html=True)
