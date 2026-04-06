def get_color(color_name):
    """Returns exact hex code from the design system."""
    colors = {
        'green': '#10B981',
        'amber': '#F59E0B',
        'red': '#EF4444',
        'off-white': '#F8FAFC',
        'slate': '#1E293B',
        'blue': '#3B82F6', 
        'gray': '#9CA3AF'  
    }
    return colors.get(color_name.lower(), '#1E293B')
