import matplotlib.pyplot as plt

# Parameters for the grid
rows, cols = 10, 10  # 10x10 grid
circle_radius = 0.4  # Radius of each circle
spacing = 1.0  # Spacing between circles

# Create the figure and axes
fig, ax = plt.subplots(figsize=(8, 8))

# Draw the circles in a grid
for row in range(rows):
    for col in range(cols):
        # Calculate circle center
        x = col * spacing
        y = row * spacing
        circle = plt.Circle((x, y), radius=circle_radius, color="blue", fill=True)
        ax.add_artist(circle)

# Add column numbers on top
for col in range(cols):
    x = col * spacing
    y = -spacing  # Position above the top row
    ax.text(x, y, str(col), ha="center", va="center", fontsize=10, color="black")

# Add row numbers on the left
for row in range(rows):
    x = -spacing  # Position to the left of the first column
    y = row * spacing
    ax.text(x, y, str(row), ha="center", va="center", fontsize=10, color="black")

# Set the aspect ratio and limits
ax.set_aspect("equal")
ax.set_xlim(-2 * spacing, cols * spacing)
ax.set_ylim(-spacing, (rows + 1) * spacing)

# Invert y-axis to have the origin at the top-left
ax.invert_yaxis()

# Hide axes for better visualization
ax.axis("off")

# Show the plot
plt.show()
