# import streamlit as st
# import plotly.graph_objects as go
# import numpy as np
# from streamlit_plotly_events import plotly_events


# # Password check function
# def check_password():
#     if st.session_state.get("password_correct", False):
#         return True

#     st.error("Unauthorized access! Please login from the main page.")
#     return False

# # Check if the password is correct before allowing access to this page
# if not check_password():
#     st.stop()


# # Caching the plot to avoid re-drawing it on every interaction
# @st.cache_data
# def draw_cricket_ground():
#     fig = go.Figure()

#     # Create circular boundaries for the cricket ground (inner circle and outer boundary)
#     inner_circle_radius = 30
#     boundary_radius = 100

#     # Add the boundary circle (green background for the field)
#     circle_x = boundary_radius * np.cos(np.linspace(0, 2 * np.pi, 100))
#     circle_y = boundary_radius * np.sin(np.linspace(0, 2 * np.pi, 100))
#     fig.add_trace(go.Scatter(x=circle_x, y=circle_y, mode='lines',
#                              fill='toself', fillcolor='lightgreen',
#                              line=dict(color='green', width=3), showlegend=False))

#     # Add the inner circle
#     inner_circle_x = inner_circle_radius * np.cos(np.linspace(0, 2 * np.pi, 100))
#     inner_circle_y = inner_circle_radius * np.sin(np.linspace(0, 2 * np.pi, 100))
#     fig.add_trace(go.Scatter(x=inner_circle_x, y=inner_circle_y, mode='lines',
#                              line=dict(color='white', width=2), showlegend=False))

#     # Add the pitch as a small rectangle in the center
#     fig.add_trace(go.Scatter(
#         x=[-5, 5, 5, -5, -5],
#         y=[-60, -60, 60, 60, -60],
#         fill="toself",
#         fillcolor="brown",
#         line=dict(color="brown"),
#         showlegend=False
#     ))

#     # Add text for "Off-Side" and "Leg-Side"
#     fig.add_annotation(x=50, y=0, text="Off-Side", showarrow=False, font=dict(size=16, color="blue"))
#     fig.add_annotation(x=-50, y=0, text="Leg-Side", showarrow=False, font=dict(size=16, color="blue"))

#     # Add an invisible background circle to capture all click events inside the boundary
#     fig.add_shape(
#         type="circle",
#         x0=-boundary_radius, y0=-boundary_radius, x1=boundary_radius, y1=boundary_radius,
#         line=dict(color="green", width=3),  # Keep it invisible
#         fillcolor="rgba(0,0,0,0)",  # Fully transparent
#         layer="below"  # Ensure this shape is below other elements
#     )

#     # Set the layout of the plot to look like a cricket ground
#     fig.update_layout(
#         width=600,
#         height=600,
#         xaxis=dict(range=[-110, 110], zeroline=False, showgrid=False, visible=False),
#         yaxis=dict(range=[-110, 110], zeroline=False, showgrid=False, visible=False),
#         plot_bgcolor='green',  # Green background to resemble a field
#         margin=dict(l=0, r=0, t=0, b=0),
#         title="Cricket Ground Wagon Wheel",
#     )

#     return fig

# # Streamlit app layout
# st.title("Cricket Wagon Wheel with Click Capture")

# # Display the cricket ground using Plotly and cache the figure
# fig = draw_cricket_ground()

# # Capture click events on the Plotly chart
# click_data = plotly_events(fig, click_event=True, override_height=600, override_width='100%')

# # Initialize session state to store click data
# if 'clicked_coords' not in st.session_state:
#     st.session_state['clicked_coords'] = []

# # Check if click_data is not empty and contains the expected keys
# if click_data and 'x' in click_data[0] and 'y' in click_data[0]:
#     x, y = click_data[0]['x'], click_data[0]['y']
#     st.session_state['clicked_coords'].append((x, y))

# # Display all captured click coordinates
# if st.session_state['clicked_coords']:
#     st.write("Shot coordinates:")
#     for coord in st.session_state['clicked_coords']:
#         st.write(f"Clicked at: {coord[0]}, {coord[1]}")
# else:
#     st.write("Click anywhere on the wagon wheel to get the coordinates.")


#===============================================================================================
#===============================================================================================

import streamlit as st

# Set the canvas size and circle radius
canvas_width = 400
canvas_height = 400
circle_radius = canvas_width // 2
inner_circle_radius = 80  # Radius of the inner circle

# Display the title
st.title("Wagon Wheel")

# Inject HTML, CSS, and JavaScript into the Streamlit app using st.components.v1.html
html_code = f"""
    <html>
    <head>
    <style>
        /* Circle to resemble a cricket ground */
        .circle {{
            width: {canvas_width}px;
            height: {canvas_height}px;
            background-color: #228B22;  /* Green background for the cricket field */
            border-radius: 50%;
            position: relative;
            cursor: pointer;
            border: 3px solid black;
            box-shadow: 0px 0px 10px 3px rgba(0,0,0,0.2);  /* Slight shadow for realism */
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        /* Adding a rectangle in the center to represent the cricket pitch */
        .pitch {{
            width: 40px;
            height: 120px;
            background-color: #d2b48c;  /* Brown color for the pitch */
            position: absolute;
        }}
        
        /* Boundary line circle */
        .boundary {{
            width: 95%;
            height: 95%;
            border: 2px dashed white; /* Dashed boundary line */
            border-radius: 50%;
            position: absolute;
            top: 2.0%;
            left: 2.0%;
        }}
        
        /* Inner circle for 30-yard circle */
        .inner-circle {{
            width: {inner_circle_radius * 2}px;
            height: {inner_circle_radius * 2}px;
            border: 2px solid white; /* Solid white for inner circle */
            border-radius: 50%;
            position: absolute;
        }}

        /* Coordinate display styling */
        .coords-display {{
            margin-top: 20px;
            font-size: 18px;
        }}
    </style>
    </head>
    <body>
        <div class="circle" id="circle">
            <div class="boundary"></div> <!-- Boundary circle -->
            <div class="inner-circle"></div> <!-- 30-yard inner circle -->
            <div class="pitch"></div>  <!-- Pitch in the center of the circle -->
        </div>
        <p id="coords" class="coords-display">Mouse Coordinates: (Click inside the circle)</p>

        <script>
            document.getElementById('circle').addEventListener('click', function(event) {{
                const circle = document.getElementById('circle');
                const circleRect = circle.getBoundingClientRect();

                // Calculate mouse coordinates relative to the top-left corner of the circle
                const mouseX = event.clientX - circleRect.left;
                const mouseY = event.clientY - circleRect.top;

                // Calculate the center of the circle
                const centerX = {circle_radius};
                const centerY = {circle_radius};

                // Convert mouse coordinates to the coordinate system where the center is (0, 0)
                const relativeX = mouseX - centerX;
                const relativeY = centerY - mouseY;  // Invert Y-axis to match quadrant system

                // Calculate the distance from the center of the circle
                const distanceFromCenter = Math.sqrt(Math.pow(relativeX, 2) + Math.pow(relativeY, 2));

                // Check if the click is inside the circle's radius
                if (distanceFromCenter <= {circle_radius}) {{
                    // Check if the click is near the boundary (within 10 pixels from the edge)
                    const boundaryThreshold = 10;
                    if (distanceFromCenter >= {circle_radius} - boundaryThreshold) {{
                        document.getElementById('coords').textContent = `Boundary hit! Coordinates: (${{relativeX}}, ${{relativeY}})`;
                    }} else {{
                        document.getElementById('coords').textContent = `Coordinates: (${{relativeX}}, ${{relativeY}})`;
                    }}
                }} else {{
                    document.getElementById('coords').textContent = `Click is outside the circle`;
                }}
            }});
        </script>
    </body>
    </html>
"""

# Render the HTML in the Streamlit app
st.components.v1.html(html_code, height=500)
