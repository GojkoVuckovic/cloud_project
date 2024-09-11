# Cloud Computing Project - 2023/2024

This project represents a web application for storing and managing movie content, developed using AWS cloud services and following cloud-native architecture principles.

## User Types

1. **Unauthenticated User**: Can register an account and log into the system if they already have an account.
2. **Administrator**: An authenticated user with the administrator role. Can upload new content, view, modify, and delete existing content.
3. **Regular User**: A regular user who successfully logs into the system. Can search and view content, rate it, subscribe to certain content, manage subscriptions, receive notifications, and access a personalized feed based on previous interactions. The user can also download uploaded content.

## System Components

- **Client Application**: Provides a graphical interface for users to interact with the system.
- **Server Application**: A cloud-native backend system that handles business logic. It should use appropriate AWS services to meet both functional and non-functional requirements.

## Functional Requirements

- **User Registration (Unauthenticated User)**:  
  Users register by providing their first name, last name, date of birth, username, email (must be unique), and password.
  
- **User Login (Unauthenticated User)**:  
  Users log in by entering their username and password to access system functionalities based on their role.

- **Upload Movie Content (Administrator)**:  
  The system stores metadata about the content, including file name, type, size, creation date, and last modified date. Additional information such as title, description, actors, directors, and genres should also be stored.

- **View Content (Administrator/Regular User)**:  
  Users can view uploaded content and its metadata, as well as watch movies through the client application.

- **Edit Content (Administrator)**:  
  Administrators can modify content or its associated metadata.

- **Delete Content (Administrator)**:  
  Administrators can delete any content, along with its metadata.

- **Search Content (Regular User)**:  
  Users can search for content based on metadata (title, description, actors, directors, and genre).

- **Download Content (Regular User)**:  
  Users can download movie content without the associated metadata.

- **Rate Content (Regular User)**:  
  Users can rate content using a minimum of 3 levels (e.g., 1-5, love/like/dislike). The specific rating system is left to the students' choice.

- **Subscribe to Content (Regular User)**:  
  Users can subscribe to content based on metadata like actors, directors, and genres. They will receive notifications when new content matching their subscriptions is added.

- **Manage Subscriptions (Regular User)**:  
  Users can view and delete their subscriptions.

- **Personalized Feed (Regular User)**:  
  Upon logging in, users receive a personalized feed based on past interactions, including ratings, subscriptions, and previous downloads. The feed updates automatically when new content is uploaded or user interactions change.

  Example 1: If a user is subscribed to the comedy genre and a new comedy is added, it will appear in the user's feed.  
  Example 2: If a user has previously watched horror films but recently prefers comedies, comedies will appear in the feed instead of horror films.

- **Transcoding Movie Content (System)**:  
  Users should be able to choose the resolution for viewing or downloading content, with at least three resolution options. The system must automatically transcode content into different resolutions when uploaded and handle potential errors during processing.

## Non-Functional Requirements

- **Cloud-Native Architecture**:  
  The system must follow cloud-native architecture principles, utilizing appropriate AWS services. An architecture diagram is required.

- **Separation of Content and Metadata**:  
  Content and metadata should be stored in appropriate storage services.

- **System Performance During Searches**:  
  The system should be optimized for performance during searches, considering data modeling and storage decisions to ensure efficient data retrieval.

- **Infrastructure as Code (IaC)**:  
  All services should be instantiated and configured using an Infrastructure as Code tool, either declaratively or imperatively.

- **Communication Style**:  
  Depending on the request flow and functionality, the system should use synchronous or asynchronous communication following event-driven architecture principles.

- **API Gateway**:  
  An API Gateway serves as the entry point for the system, providing a REST API for communication between the client and server applications.

- **Frontend Deployment**:  
  The frontend application should be publicly accessible and allow users to interact with the system.

- **Notification System**:  
  Users receive notifications when new content is uploaded to which they are subscribed. Notifications should include basic information about the content.