# PMS
PMS is a hierarchical project management platform designed to streamline complex workflows by breaking projects into milestones, tasks, and actionable steps. It integrates team collaboration, real-time communication, file management, and analytics to ensure transparency, accountability, and efficiency across all project stages.

Core Functionalities
1. Project Creation and Management
Description: Users can create projects with details (name, description, deadlines, priority).

Features:

        Hierarchical structure (Project → Milestones → Tasks → Steps/Issues).
        
        Customizable project templates.

Dashboard for tracking progress (Gantt charts, Kanban boards).
<img width="1079" alt="Screenshot 2025-02-03 162812" src="https://github.com/user-attachments/assets/2f73ee3a-31c7-459e-9298-85dee3feb7eb" />



2. Milestone Creation and Management
Description: Divide projects into phases (milestones) with deadlines and dependencies.

Features:

        Set dependencies between milestones.
        
        Track completion status and delays.
<img width="992" alt="Screenshot 2025-02-03 161909" src="https://github.com/user-attachments/assets/e0caff22-bfc5-4d79-9171-e083088b679e" />

3. Task Creation and Management
Description: Break milestones into smaller tasks with assignees, deadlines, and priorities.

Features:

        Drag-and-drop task prioritization.
        
        Task labels (e.g., "Urgent," "In Review").
<img width="1005" alt="Screenshot 2025-02-03 162017" src="https://github.com/user-attachments/assets/b120d312-38a0-44f0-be4a-7b734cb179de" />

4. Task Steps & Issue Management
Description: Divide tasks into sub-steps and log issues (bugs, blockers).

Features:

        Step completion checklists.
        
        Issue tagging (e.g., "Critical," "Resolved").
<img width="952" alt="Screenshot 2025-02-03 162543" src="https://github.com/user-attachments/assets/9c28dd1b-7142-4c42-8d0d-14c105caa46c" />
<img width="1001" alt="Screenshot 2025-02-03 162142" src="https://github.com/user-attachments/assets/a6c593cc-2f2f-4940-97c0-da2ec0e1bba4" />

5. User Management
Description: Admin-controlled user profiles with roles (Admin, Staff, viewer) and Staff further divided in to team leader and member 


Features:
        Permission management 
        Profile customization .
<img width="995" alt="Screenshot 2025-02-03 162844" src="https://github.com/user-attachments/assets/ea1c338d-12d2-4a3d-8df9-e4c7a9cc649a" />

6. Team Creation & Management
Description: Create teams  with designated leaders.

Features:
        Team-specific dashboards.        
       
<img width="1000" alt="Screenshot 2025-02-03 162824" src="https://github.com/user-attachments/assets/b63acd3e-4850-4c15-9688-8596d98de389" />

7. Assign Teams to Projects
Description: Link teams to projects for centralized collaboration.

Features:
        Team workload analytics.
        Overlap warnings for conflicting assignments.

8. Assign Tasks to Team Members
Description: Allocate tasks to individuals with deadlines and priority levels.

Features:
        Auto-assignment based on skills/availability.
        Task delegation history.

9. User Permissions & Roles
Description: Role-based access control (RBAC) for data security.

Features:
        Custom roles (e.g., "Viewer" "Admin", "Staff").
        Granular permissions (e.g., "Edit Tasks," "Delete Files","add files", "can delete" ...).

10. File Management System
Description: Centralized storage for project-related documents, images, and code.
<img width="1001" alt="Screenshot 2025-02-03 162951" src="https://github.com/user-attachments/assets/e3cae7ee-8c75-44f4-ad12-5dcd35dacb5d" />

11. Real-Time Chat Rooms per Project
Description: Dedicated chat channels for instant team communication.

Features:
      File sharing in chats.
      @mentions .
      replies,
      
<img width="1010" alt="Screenshot 2025-02-03 163009" src="https://github.com/user-attachments/assets/7fd8a5a7-b972-4fe6-989b-4b11cd999929" />

12. Activity Logs
Description: Audit trails for all user actions (e.g., "User X updated Task Y").
Features:
       Filter logs by user, project, or date.
       Export logs for compliance.
<img width="1010" alt="Screenshot 2025-02-03 162856" src="https://github.com/user-attachments/assets/00647d56-b49f-42f2-a9e2-a376a373674c" />

13. Notification System
Description: Real-time alerts for deadlines, updates, and mentions.

Features:
       Email, in-app, and mobile push notifications.
       Custom notification schedules.

14. Report Generation
Description: Generate analytics for projects, teams, and users.

Features:
Customizable PDF/Excel exports.
<img width="998" alt="Screenshot 2025-02-03 162630" src="https://github.com/user-attachments/assets/2348250f-ae1a-4cd0-8530-6689552cbea1" />
<img width="949" alt="Screenshot 2025-02-03 162617" src="https://github.com/user-attachments/assets/b93fb3ed-e942-4031-86bc-5d7d420d05a3" />

Technical Components
Backend: Django.

Frontend: Bootstrap 5  and jquery.

Database: MySQL.

Real-Time Features: WebSocket (Socket.io) for chat/notifications.

Benefits for Users
Transparency: Track progress at all levels (project → step).

Efficiency: Reduce manual coordination with automated workflows.

Collaboration: Centralize communication and files.

Scalability: Manage small teams or enterprise-level projects.

Conclusion
PMS is a unified solution for organizations to manage projects, teams, and resources with precision. By combining task granularity, real-time collaboration, and robust analytics, it empowers teams to deliver projects faster and with fewer roadblocks.

Let me know if you need help drafting specific sections or refining this further!
