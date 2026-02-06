# UML Sequence Diagrams

This directory contains comprehensive UML sequence diagrams for the OrbitLink FYP 2025 application. The diagrams are written in PlantUML format and document the interaction flows between users, UI components, controllers, repositories, and entities.

## Diagrams Overview

### User Management Flows

1. **view_personal_profile.puml** - User profile viewing
   - Actor: Business User
   - Components: ProfileUI, UserController, RegisteredUser
   - Flow: Retrieves and displays user profile data from session

2. **change_username.puml** - Username modification
   - Actor: Business User
   - Components: ChangeUsernameUI, UserController, RegisteredUser
   - Flow: Validates and updates username with success/failure handling

3. **change_password.puml** - Password change
   - Actor: Business User
   - Components: ChangePasswordUI, UserController, RegisteredUser
   - Flow: Verifies current password, hashes new password, updates database

4. **log_out.puml** - User logout
   - Actor: Business User
   - Components: UserUI
   - Flow: Clears session and redirects to landing page

5. **delete_account.puml** - Account deletion
   - Actor: Business User
   - Components: ProfileUI, UserController, RegisteredUser
   - Flow: Confirms deletion, removes user from database, clears session

### Project Management Flows

6. **view_personal_dashboard.puml** - Dashboard with recent projects
   - Actor: Business User
   - Components: ProjectsDashboardUI, ProjectsController, ProjectRepository, Project
   - Flow: Retrieves and displays 3 most recently opened projects

7. **create_new_project.puml** - New project creation
   - Actor: Business User
   - Components: ProjectsCreateUI, ProjectsController, ProjectRepository, Project
   - Flow: Validates input, creates project in MongoDB, returns to projects list

8. **view_projects.puml** - Projects list viewing
   - Actor: Business User
   - Components: ProjectsListUI, ProjectsController, ProjectRepository, Project
   - Flow: Displays all projects or filtered results based on search query

### Social Network Analysis Flows

9. **detect_communities.puml** - Community detection
   - Actor: Business User
   - Components: DetectCommunitiesUI
   - Flow: Displays algorithm options and network visualization with metrics

10. **view_network_graph.puml** - Network graph visualization
    - Actor: Business User
    - Components: NetworkGraphUI
    - Flow: Renders interactive network with nodes, edges, and community clusters

11. **export_graph_pdf.puml** - Graph export functionality
    - Actor: Business User
    - Components: ExportUI
    - Flow: Generates and downloads PDF/PNG of current graph

## How to View/Render the Diagrams

### Method 1: Online PlantUML Viewer

1. Visit [PlantUML Online Editor](https://www.plantuml.com/plantuml/uml/)
2. Copy the content of any `.puml` file
3. Paste it into the editor
4. The diagram will render automatically
5. You can download as PNG, SVG, or other formats

### Method 2: Visual Studio Code Extension

1. Install the "PlantUML" extension by jebbs
2. Install Java Runtime Environment (JRE) if not already installed
3. Open any `.puml` file in VS Code
4. Press `Alt+D` (or `Cmd+D` on Mac) to preview the diagram
5. Right-click on the preview to export as PNG, SVG, etc.

### Method 3: Command Line with PlantUML

1. Download PlantUML JAR from [PlantUML Download](https://plantuml.com/download)
2. Install Java Runtime Environment (JRE)
3. Generate diagram images:
   ```bash
   java -jar plantuml.jar view_personal_profile.puml
   ```
4. This creates a PNG file in the same directory

### Method 4: IntelliJ IDEA / PyCharm

1. Install the "PlantUML Integration" plugin
2. Open any `.puml` file
3. The diagram will render in a preview pane
4. Right-click to export or save images

### Method 5: GitHub Integration

GitHub automatically renders PlantUML diagrams in markdown files:

```markdown
![Diagram](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/GTMGRADE/orbitlink-fyp-2025/main/docs/sequence_diagrams/view_personal_profile.puml)
```

## Diagram Structure

All diagrams follow a consistent structure:

1. **Component Definitions**: Participants (actors, UI, controllers, entities, repositories)
2. **Activation Boxes**: Show when components are active during method execution
3. **Method Signatures**: Include return types and parameters where applicable
4. **Alt Blocks**: Handle success/failure scenarios and conditional logic
5. **Return Values**: Show data returned on dashed return arrows
6. **Notes**: Provide additional context where needed

## Technical Requirements

- **PlantUML Version**: Compatible with PlantUML v1.2020.0 and later
- **Java**: JRE 8 or later (for local rendering)
- **Syntax**: Standard PlantUML sequence diagram syntax

## Maintenance

When updating the codebase:

1. Review affected sequence diagrams
2. Update component names if classes/methods are renamed
3. Update flows if interaction patterns change
4. Keep method signatures synchronized with actual code
5. Add alt blocks for new error handling scenarios

## Related Files

The diagrams are based on the following source files:

- `boundary/user_ui.py` - User interface endpoints
- `boundary/projects_ui.py` - Project interface endpoints
- `Controller/user_controller.py` - User business logic
- `Controller/projects_controller.py` - Project business logic
- `entity/project.py` - Project entity and repository
- `entity/user.py` - User entity

## Notes

- All dates are formatted as dd/mm/yy in the UI
- Session data includes user_id and user_type
- MongoDB is used for project persistence
- In-memory storage is used for user data (demo mode)
- Community detection and network visualization use JavaScript libraries for frontend rendering

## Contributing

When adding new features:

1. Create a new `.puml` file following the naming convention
2. Use the same component styling and structure
3. Include activation boxes and proper return types
4. Add alt blocks for error scenarios
5. Update this README with the new diagram description
