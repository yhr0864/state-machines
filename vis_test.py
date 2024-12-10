import matplotlib.pyplot as plt

# Parameters for the grid
rows, cols = 10, 10  # 10x10 grid
circle_radius = 0.4  # Radius of each circle
spacing = 1.0  # Spacing between circles

# Create the figure and axes
fig, ax = plt.subplots(figsize=(6, 6))

# Draw the circles in a grid
for row in range(rows):
    for col in range(cols):
        # Calculate circle center
        x = col * spacing
        y = row * spacing
        circle = plt.Circle((x, y), radius=circle_radius, color="blue", fill=True)
        ax.add_artist(circle)

# Set the aspect ratio and limits
ax.set_aspect("equal")
ax.set_xlim(-spacing, cols * spacing)
ax.set_ylim(-spacing, rows * spacing)

# Hide axes for better visualization
ax.axis("off")

# Show the plot
plt.show()
