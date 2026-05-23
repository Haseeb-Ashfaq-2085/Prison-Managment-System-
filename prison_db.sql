-- =============================================
-- PRISON MANAGEMENT SYSTEM - DATABASE SCHEMA
-- =============================================
USE PrisonManagement;
GO

-- =============================================
-- DROP EXISTING OBJECTS
-- =============================================

-- Drop Stored Procedures
DROP PROCEDURE IF EXISTS sp_LoginUser;
DROP PROCEDURE IF EXISTS sp_RegisterUser;
DROP PROCEDURE IF EXISTS sp_GetDashboardStats;
DROP PROCEDURE IF EXISTS sp_GetAllPrisoners;
DROP PROCEDURE IF EXISTS sp_GetPrisonerByID;
DROP PROCEDURE IF EXISTS sp_AddPrisoner;
DROP PROCEDURE IF EXISTS sp_UpdatePrisoner;
DROP PROCEDURE IF EXISTS sp_SearchPrisoners;
DROP PROCEDURE IF EXISTS sp_GetAllCells;
DROP PROCEDURE IF EXISTS sp_AddCell;
DROP PROCEDURE IF EXISTS sp_UpdateCell;
DROP PROCEDURE IF EXISTS sp_GetOvercrowdedCells;
DROP PROCEDURE IF EXISTS sp_GetReleaseDuePrisoners;
DROP PROCEDURE IF EXISTS sp_GetAllMedicalRecords;
DROP PROCEDURE IF EXISTS sp_GetMedicalRecordsByPrisoner;
DROP PROCEDURE IF EXISTS sp_AddMedicalRecord;
DROP PROCEDURE IF EXISTS sp_GetMedicalSchedule;
DROP PROCEDURE IF EXISTS sp_RegisterVisitor;
DROP PROCEDURE IF EXISTS sp_GetAllVisitors;
DROP PROCEDURE IF EXISTS sp_GetVisitorByCNIC;
DROP PROCEDURE IF EXISTS sp_ScheduleVisit;
DROP PROCEDURE IF EXISTS sp_GetAllVisitorLogs;
DROP PROCEDURE IF EXISTS sp_GetVisitorHistory;
DROP PROCEDURE IF EXISTS sp_GetVisitorLogsByDate;
DROP PROCEDURE IF EXISTS sp_GetRecentAdmissions;
DROP PROCEDURE IF EXISTS sp_GetActivityLog;
DROP PROCEDURE IF EXISTS sp_GetPrisonersByStatus;
DROP PROCEDURE IF EXISTS sp_TransferPrisoner;
DROP PROCEDURE IF EXISTS sp_GetAllUsers;
DROP PROCEDURE IF EXISTS sp_GetSecurityOfficers;
DROP PROCEDURE IF EXISTS sp_GetDoctors;
DROP PROCEDURE IF EXISTS sp_AssignOfficerToCell;
DROP PROCEDURE IF EXISTS sp_GetPendingVisits;
DROP PROCEDURE IF EXISTS sp_ApproveVisit;
DROP PROCEDURE IF EXISTS sp_RejectVisit;
DROP PROCEDURE IF EXISTS sp_RequestVisit;
DROP PROCEDURE IF EXISTS sp_GetVisitsByStatus;
DROP PROCEDURE IF EXISTS sp_GetAllSecurityOfficers;
GO

-- Drop Views
DROP VIEW IF EXISTS vw_PrisonerSummary;
DROP VIEW IF EXISTS vw_CellOccupancy;
GO

-- Drop Tables
DROP TABLE IF EXISTS ActivityLog;
DROP TABLE IF EXISTS VisitorLogs;
DROP TABLE IF EXISTS Visitors;
DROP TABLE IF EXISTS MedicalRecords;
DROP TABLE IF EXISTS Prisoners;
DROP TABLE IF EXISTS Cells;
DROP TABLE IF EXISTS Users;
GO

-- =============================================
-- CREATE TABLES
-- =============================================

CREATE TABLE Users (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    FullName VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Password VARCHAR(100) NOT NULL,
    Role VARCHAR(20) NOT NULL CHECK (Role IN ('Admin', 'Security', 'Medical', 'Visitor')),
    AssignedCell VARCHAR(10),
    Shift VARCHAR(20) CHECK (Shift IN ('Morning', 'Evening', 'Night', NULL)),
    Specialization VARCHAR(100),
    Status VARCHAR(20) DEFAULT 'Active' CHECK (Status IN ('Active', 'Inactive')),
    CreatedDate DATETIME DEFAULT GETDATE(),
    LastLogin DATETIME
);

CREATE TABLE Cells (
    CellID INT IDENTITY(1,1) PRIMARY KEY,
    CellNumber VARCHAR(10) UNIQUE NOT NULL,
    Capacity INT NOT NULL CHECK (Capacity > 0),
    CurrentOccupancy INT DEFAULT 0 CHECK (CurrentOccupancy >= 0),
    Block VARCHAR(10) NOT NULL,
    AssignedOfficer VARCHAR(100),
    Status VARCHAR(20) DEFAULT 'Active' CHECK (Status IN ('Active', 'Inactive', 'Maintenance'))
);

CREATE TABLE Prisoners (
    PrisonerID INT IDENTITY(1,1) PRIMARY KEY,
    FullName VARCHAR(100) NOT NULL,
    CNIC VARCHAR(15) UNIQUE NOT NULL,
    DateOfBirth DATE NOT NULL,
    Gender VARCHAR(10) NOT NULL CHECK (Gender IN ('Male', 'Female', 'Other')),
    CellID INT,
    AdmissionDate DATE NOT NULL,
    SentenceYears INT NOT NULL CHECK (SentenceYears > 0),
    RemissionDays INT DEFAULT 0 CHECK (RemissionDays >= 0),
    ReleaseDate DATE,
    Status VARCHAR(20) DEFAULT 'Active' CHECK (Status IN ('Active', 'Released', 'Transferred', 'Deceased')),
    Crime VARCHAR(200) NOT NULL,
    Address VARCHAR(300),
    EmergencyContact VARCHAR(15),
    FOREIGN KEY (CellID) REFERENCES Cells(CellID)
);

CREATE TABLE MedicalRecords (
    RecordID INT IDENTITY(1,1) PRIMARY KEY,
    PrisonerID INT NOT NULL,
    Diagnosis VARCHAR(200) NOT NULL,
    Medication VARCHAR(200),
    DoctorName VARCHAR(100) NOT NULL,
    CheckupDate DATE NOT NULL,
    NextCheckup DATE,
    Notes VARCHAR(500),
    FOREIGN KEY (PrisonerID) REFERENCES Prisoners(PrisonerID) ON DELETE CASCADE
);

CREATE TABLE Visitors (
    VisitorID INT IDENTITY(1,1) PRIMARY KEY,
    FullName VARCHAR(100) NOT NULL,
    CNIC VARCHAR(15) UNIQUE NOT NULL,
    Phone VARCHAR(15) NOT NULL,
    Relationship VARCHAR(50) NOT NULL,
    Address VARCHAR(300),
    Status VARCHAR(20) DEFAULT 'Active' CHECK (Status IN ('Active', 'Banned', 'Suspended'))
);

CREATE TABLE VisitorLogs (
    LogID INT IDENTITY(1,1) PRIMARY KEY,
    PrisonerID INT NOT NULL,
    VisitorID INT NOT NULL,
    VisitDate DATE NOT NULL,
    VisitTime TIME NOT NULL,
    Purpose VARCHAR(200),
    ApprovedBy VARCHAR(100),
    Status VARCHAR(20) DEFAULT 'Pending' CHECK (Status IN ('Pending', 'Approved', 'Rejected', 'Completed', 'Cancelled')),
    FOREIGN KEY (PrisonerID) REFERENCES Prisoners(PrisonerID) ON DELETE CASCADE,
    FOREIGN KEY (VisitorID) REFERENCES Visitors(VisitorID) ON DELETE CASCADE
);

CREATE TABLE ActivityLog (
    LogID INT IDENTITY(1,1) PRIMARY KEY,
    UserID INT,
    Action VARCHAR(200) NOT NULL,
    Description VARCHAR(500),
    TableAffected VARCHAR(50),
    RecordID INT,
    Timestamp DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

GO

-- =============================================
-- CREATE TRIGGERS
-- =============================================

CREATE TRIGGER trg_CalculateReleaseDate
ON Prisoners
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE P
    SET ReleaseDate = DATEADD(DAY, -P.RemissionDays, DATEADD(YEAR, P.SentenceYears, P.AdmissionDate))
    FROM Prisoners P
    INNER JOIN inserted i ON P.PrisonerID = i.PrisonerID;
END;
GO

CREATE TRIGGER trg_UpdateCellOccupancy
ON Prisoners
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Update affected cells
    UPDATE C
    SET CurrentOccupancy = (
        SELECT COUNT(*) 
        FROM Prisoners P 
        WHERE P.CellID = C.CellID 
        AND P.Status = 'Active'
    )
    FROM Cells C
    WHERE C.CellID IN (
        SELECT DISTINCT CellID FROM inserted
        UNION
        SELECT DISTINCT CellID FROM deleted
    );
END;
GO

-- =============================================
-- STORED PROCEDURES - AUTHENTICATION
-- =============================================

CREATE PROCEDURE sp_LoginUser
    @Email VARCHAR(100),
    @Password VARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @UserID INT, @Role VARCHAR(20), @FullName VARCHAR(100);
    
    SELECT 
        @UserID = UserID, 
        @Role = Role,
        @FullName = FullName
    FROM Users
    WHERE Email = @Email 
    AND Password = @Password 
    AND Status = 'Active';
    
    IF @UserID IS NOT NULL
    BEGIN
        UPDATE Users 
        SET LastLogin = GETDATE() 
        WHERE UserID = @UserID;
        
        INSERT INTO ActivityLog (UserID, Action, Description)
        VALUES (@UserID, 'Login', @Role + ' user logged in: ' + @Email);
        
        SELECT 
            @UserID AS UserID, 
            @FullName AS FullName,
            @Role AS Role, 
            'SUCCESS' AS Message;
    END
    ELSE
    BEGIN
        SELECT 
            NULL AS UserID, 
            NULL AS FullName,
            NULL AS Role, 
            'Invalid credentials' AS Message;
    END
END;
GO

CREATE PROCEDURE sp_RegisterUser
    @FullName VARCHAR(100),
    @Email VARCHAR(100),
    @Password VARCHAR(100),
    @Role VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    
    IF EXISTS (SELECT 1 FROM Users WHERE Email = @Email)
    BEGIN
        SELECT 'Email already exists' AS Message, 0 AS Success;
        RETURN;
    END
    
    INSERT INTO Users (FullName, Email, Password, Role, Status)
    VALUES (@FullName, @Email, @Password, @Role, 'Active');
    
    INSERT INTO ActivityLog (Action, Description)
    VALUES ('User Registration', 'New ' + @Role + ' user registered: ' + @Email);
    
    SELECT 'SUCCESS: Account created' AS Message, 1 AS Success;
END;
GO

-- =============================================
-- STORED PROCEDURES - DASHBOARD
-- =============================================

CREATE PROCEDURE sp_GetDashboardStats
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        (SELECT COUNT(*) FROM Prisoners WHERE Status = 'Active') AS ActivePrisoners,
        (SELECT COUNT(*) FROM Cells) AS TotalCells,
        (SELECT AVG(CAST(CurrentOccupancy AS FLOAT) * 100.0 / NULLIF(Capacity,0)) 
         FROM Cells WHERE Capacity > 0) AS AvgOccupancy,
        (SELECT COUNT(*) FROM Prisoners 
         WHERE ReleaseDate <= DATEADD(DAY, 30, GETDATE()) 
         AND Status = 'Active') AS UpcomingReleases,
        (SELECT COUNT(*) FROM MedicalRecords 
         WHERE NextCheckup BETWEEN GETDATE() AND DATEADD(DAY, 7, GETDATE())) AS UpcomingCheckups,
        (SELECT COUNT(*) FROM VisitorLogs 
         WHERE VisitDate = CAST(GETDATE() AS DATE)) AS TodayVisits,
        (SELECT COUNT(*) FROM Users WHERE Status = 'Active') AS ActiveUsers,
        (SELECT COUNT(*) FROM Users WHERE Role = 'Security' AND Status = 'Active') AS SecurityOfficers,
        (SELECT COUNT(*) FROM Users WHERE Role = 'Medical' AND Status = 'Active') AS Doctors,
        (SELECT COUNT(*) FROM VisitorLogs WHERE Status = 'Pending') AS PendingVisits;
END;
GO

-- =============================================
-- STORED PROCEDURES - PRISONERS
-- =============================================

CREATE PROCEDURE sp_GetAllPrisoners
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        P.PrisonerID,
        P.FullName,
        P.CNIC,
        P.DateOfBirth,
        P.Gender,
        P.AdmissionDate,
        P.SentenceYears,
        P.RemissionDays,
        P.ReleaseDate,
        P.Status,
        P.Crime,
        P.Address,
        P.EmergencyContact,
        C.CellNumber,
        C.Block,
        C.AssignedOfficer
    FROM Prisoners P
    LEFT JOIN Cells C ON P.CellID = C.CellID
    ORDER BY P.PrisonerID DESC;
END;
GO

CREATE PROCEDURE sp_GetPrisonerByID
    @PrisonerID INT
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        P.*,
        C.CellNumber,
        C.Block,
        C.AssignedOfficer
    FROM Prisoners P
    LEFT JOIN Cells C ON P.CellID = C.CellID
    WHERE P.PrisonerID = @PrisonerID;
END;
GO

CREATE PROCEDURE sp_AddPrisoner
    @FullName VARCHAR(100),
    @CNIC VARCHAR(15),
    @DateOfBirth DATE,
    @Gender VARCHAR(10),
    @CellID INT,
    @AdmissionDate DATE,
    @SentenceYears INT,
    @Crime VARCHAR(200),
    @Address VARCHAR(300),
    @EmergencyContact VARCHAR(15)
AS
BEGIN
    SET NOCOUNT ON;
    
    IF EXISTS (SELECT 1 FROM Prisoners WHERE CNIC = @CNIC)
    BEGIN
        SELECT 'CNIC already exists' AS Message, 0 AS Success;
        RETURN;
    END
    
    DECLARE @CurrentOccupancy INT, @Capacity INT;
    SELECT @CurrentOccupancy = CurrentOccupancy, @Capacity = Capacity
    FROM Cells WHERE CellID = @CellID;
    
    IF @CurrentOccupancy >= @Capacity
    BEGIN
        SELECT 'Cell is at full capacity' AS Message, 0 AS Success;
        RETURN;
    END
    
    INSERT INTO Prisoners (FullName, CNIC, DateOfBirth, Gender, CellID, AdmissionDate, 
                          SentenceYears, Crime, Address, EmergencyContact)
    VALUES (@FullName, @CNIC, @DateOfBirth, @Gender, @CellID, @AdmissionDate, 
            @SentenceYears, @Crime, @Address, @EmergencyContact);
    
    INSERT INTO ActivityLog (Action, Description)
    VALUES ('Prisoner Added', 'New prisoner: ' + @FullName + ' (' + @CNIC + ')');
    
    SELECT 'Prisoner added successfully' AS Message, 1 AS Success;
END;
GO

CREATE PROCEDURE sp_UpdatePrisoner
    @PrisonerID INT,
    @RemissionDays INT = NULL,
    @Status VARCHAR(20) = NULL,
    @CellID INT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    IF @RemissionDays IS NOT NULL
        UPDATE Prisoners SET RemissionDays = RemissionDays + @RemissionDays
        WHERE PrisonerID = @PrisonerID;
    
    IF @Status IS NOT NULL
        UPDATE Prisoners SET Status = @Status
        WHERE PrisonerID = @PrisonerID;
    
    IF @CellID IS NOT NULL
        UPDATE Prisoners SET CellID = @CellID
        WHERE PrisonerID = @PrisonerID;
    
    INSERT INTO ActivityLog (Action, Description)
    VALUES ('Prisoner Updated', 'Prisoner ID: ' + CAST(@PrisonerID AS VARCHAR));
    
    SELECT 'Prisoner updated successfully' AS Message, 1 AS Success;
END;
GO

CREATE PROCEDURE sp_SearchPrisoners
    @SearchTerm VARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        P.PrisonerID,
        P.FullName,
        P.CNIC,
        P.Status,
        P.Crime,
        C.CellNumber,
        C.Block
    FROM Prisoners P
    LEFT JOIN Cells C ON P.CellID = C.CellID
    WHERE P.FullName LIKE '%' + @SearchTerm + '%'
       OR P.CNIC LIKE '%' + @SearchTerm + '%'
       OR P.Crime LIKE '%' + @SearchTerm + '%'
    ORDER BY P.PrisonerID DESC;
END;
GO

CREATE PROCEDURE sp_GetPrisonersByStatus
    @Status VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        P.PrisonerID,
        P.FullName,
        P.CNIC,
        P.AdmissionDate,
        P.ReleaseDate,
        C.CellNumber,
        C.Block
    FROM Prisoners P
    LEFT JOIN Cells C ON P.CellID = C.CellID
    WHERE P.Status = @Status
    ORDER BY P.AdmissionDate DESC;
END;
GO

CREATE PROCEDURE sp_TransferPrisoner
    @PrisonerID INT,
    @NewCellID INT
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @CurrentOccupancy INT, @Capacity INT;
    SELECT @CurrentOccupancy = CurrentOccupancy, @Capacity = Capacity
    FROM Cells WHERE CellID = @NewCellID;
    
    IF @CurrentOccupancy >= @Capacity
    BEGIN
        SELECT 'Target cell is at full capacity' AS Message, 0 AS Success;
        RETURN;
    END
    
    UPDATE Prisoners SET CellID = @NewCellID
    WHERE PrisonerID = @PrisonerID;
    
    INSERT INTO ActivityLog (Action, Description)
    VALUES ('Prisoner Transferred', 'Prisoner ID: ' + CAST(@PrisonerID AS VARCHAR));
    
    SELECT 'Prisoner transferred successfully' AS Message, 1 AS Success;
END;
GO

CREATE PROCEDURE sp_GetReleaseDuePrisoners
    @Days INT = 30
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        P.PrisonerID,
        P.FullName,
        P.CNIC,
        P.ReleaseDate,
        C.CellNumber,
        C.Block
    FROM Prisoners P
    LEFT JOIN Cells C ON P.CellID = C.CellID
    WHERE P.ReleaseDate <= DATEADD(DAY, @Days, GETDATE())
      AND P.Status = 'Active'
    ORDER BY P.ReleaseDate;
END;
GO

CREATE PROCEDURE sp_GetRecentAdmissions
    @Days INT = 30
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT TOP 10
        P.FullName,
        P.CNIC,
        P.AdmissionDate,
        P.Crime,
        P.Status,
        C.CellNumber
    FROM Prisoners P
    LEFT JOIN Cells C ON P.CellID = C.CellID
    WHERE P.AdmissionDate >= DATEADD(DAY, -@Days, GETDATE())
    ORDER BY P.AdmissionDate DESC;
END;
GO

-- =============================================
-- STORED PROCEDURES - CELLS
-- =============================================

CREATE PROCEDURE sp_GetAllCells
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        CellID,
        CellNumber,
        Capacity,
        CurrentOccupancy,
        Block,
        AssignedOfficer,
        Status,
        CAST(CASE 
            WHEN Capacity > 0 THEN (CurrentOccupancy * 100.0 / Capacity)
            ELSE 0 
        END AS DECIMAL(5,2)) AS OccupancyPercent
    FROM Cells
    ORDER BY Block, CellNumber;
END;
GO

CREATE PROCEDURE sp_AddCell
    @CellNumber VARCHAR(10),
    @Capacity INT,
    @Block VARCHAR(10),
    @OfficerID INT
AS
BEGIN
    SET NOCOUNT ON;
    
    IF EXISTS (SELECT 1 FROM Cells WHERE CellNumber = @CellNumber)
    BEGIN
        SELECT 'Cell number already exists' AS Message, 0 AS Success;
        RETURN;
    END
    
    DECLARE @OfficerName VARCHAR(100);
    SELECT @OfficerName = FullName
    FROM Users
    WHERE UserID = @OfficerID AND Role = 'Security' AND Status = 'Active';
    
    INSERT INTO Cells (CellNumber, Capacity, Block, AssignedOfficer)
    VALUES (@CellNumber, @Capacity, @Block, @OfficerName);
    
    SELECT 'Cell added & officer assigned' AS Message, 1 AS Success;
END;
GO

UPDATE Cells SET AssignedOfficer = 'Officer Hassan Raza' WHERE CellNumber = 'A-101';
UPDATE Cells SET AssignedOfficer = 'Officer Imran Khan' WHERE CellNumber = 'A-102';
UPDATE Cells SET AssignedOfficer = 'Officer Kamran Ali' WHERE CellNumber = 'A-103';
UPDATE Cells SET AssignedOfficer = 'Officer Bilal Ahmed' WHERE CellNumber = 'B-201';
UPDATE Cells SET AssignedOfficer = 'Officer Usman Tariq' WHERE CellNumber = 'B-202';
UPDATE Cells SET AssignedOfficer = 'Officer Shahid Malik' WHERE CellNumber = 'C-301';
UPDATE Cells SET AssignedOfficer = 'Officer Zahid Abbas' WHERE CellNumber = 'C-302';
GO

CREATE PROCEDURE sp_UpdateCell
    @CellID INT,
    @OfficerID INT = NULL,
    @Capacity INT = NULL,
    @Status VARCHAR(20) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRY
        IF NOT EXISTS (SELECT 1 FROM Cells WHERE CellID = @CellID)
        BEGIN
            SELECT 'Cell not found' AS Message, 0 AS Success;
            RETURN;
        END
        
        IF @OfficerID IS NOT NULL
        BEGIN
            DECLARE @OfficerName VARCHAR(100);
            SELECT @OfficerName = FullName
            FROM Users
            WHERE UserID = @OfficerID AND Role = 'Security' AND Status = 'Active';
            
            IF @OfficerName IS NOT NULL
                UPDATE Cells SET AssignedOfficer = @OfficerName WHERE CellID = @CellID;
            ELSE
            BEGIN
                SELECT 'Officer not found' AS Message, 0 AS Success;
                RETURN;
            END
        END
        
        IF @Capacity IS NOT NULL
        BEGIN
            DECLARE @CurrentOccupancy INT;
            SELECT @CurrentOccupancy = CurrentOccupancy FROM Cells WHERE CellID = @CellID;
            
            IF @Capacity < @CurrentOccupancy
            BEGIN
                SELECT 'Capacity cannot be less than occupancy' AS Message, 0 AS Success;
                RETURN;
            END
            
            UPDATE Cells SET Capacity = @Capacity WHERE CellID = @CellID;
        END
        
        IF @Status IS NOT NULL
            UPDATE Cells SET Status = @Status WHERE CellID = @CellID;
        
        INSERT INTO ActivityLog (Action, Description)
        VALUES ('Cell Updated', 'Cell ID: ' + CAST(@CellID AS VARCHAR));
        
        SELECT 'Cell updated successfully' AS Message, 1 AS Success;
    END TRY
    BEGIN CATCH
        SELECT ERROR_MESSAGE() AS Message, 0 AS Success;
    END CATCH
END;
GO


CREATE PROCEDURE sp_GetOvercrowdedCells
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        CellNumber,
        Block,
        Capacity,
        CurrentOccupancy,
        AssignedOfficer,
        CAST((CurrentOccupancy * 100.0 / Capacity) AS DECIMAL(5,2)) AS OccupancyPercent
    FROM Cells
    WHERE CurrentOccupancy > Capacity
    ORDER BY OccupancyPercent DESC;
END;
GO

CREATE PROCEDURE sp_AssignOfficerToCell
    @OfficerName VARCHAR(100),
    @CellNumber VARCHAR(10)
AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE Cells
    SET AssignedOfficer = @OfficerName
    WHERE CellNumber = @CellNumber;
    
    SELECT 'Officer assigned successfully' AS Message;
END;
GO

-- =============================================
-- STORED PROCEDURES - MEDICAL
-- =============================================

CREATE PROCEDURE sp_GetAllMedicalRecords
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        M.RecordID,
        M.PrisonerID,
        P.FullName,
        P.CNIC,
        M.Diagnosis,
        M.Medication,
        M.DoctorName,
        M.CheckupDate,
        M.NextCheckup,
        M.Notes
    FROM MedicalRecords M
    INNER JOIN Prisoners P ON M.PrisonerID = P.PrisonerID
    ORDER BY M.CheckupDate DESC;
END;
GO

CREATE PROCEDURE sp_GetMedicalRecordsByPrisoner
    @PrisonerID INT
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        RecordID,
        Diagnosis,
        Medication,
        DoctorName,
        CheckupDate,
        NextCheckup,
        Notes
    FROM MedicalRecords
    WHERE PrisonerID = @PrisonerID
    ORDER BY CheckupDate DESC;
END;
GO

CREATE PROCEDURE sp_AddMedicalRecord
    @PrisonerID INT,
    @Diagnosis VARCHAR(200),
    @Medication VARCHAR(200),
    @DoctorName VARCHAR(100),
    @CheckupDate DATE,
    @NextCheckup DATE,
    @Notes VARCHAR(500)
AS
BEGIN
    SET NOCOUNT ON;
    
    INSERT INTO MedicalRecords (PrisonerID, Diagnosis, Medication, DoctorName, 
                               CheckupDate, NextCheckup, Notes)
    VALUES (@PrisonerID, @Diagnosis, @Medication, @DoctorName, 
            @CheckupDate, @NextCheckup, @Notes);
    
    INSERT INTO ActivityLog (Action, Description)
    VALUES ('Medical Record Added', 'For Prisoner ID: ' + CAST(@PrisonerID AS VARCHAR));
    
    SELECT 'Medical record added successfully' AS Message, 1 AS Success;
END;
GO

CREATE PROCEDURE sp_GetMedicalSchedule
    @Days INT = 7
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        M.RecordID,
        P.FullName,
        P.CNIC,
        M.Diagnosis,
        M.Medication,
        M.NextCheckup,
        C.CellNumber,
        M.DoctorName
    FROM MedicalRecords M
    INNER JOIN Prisoners P ON M.PrisonerID = P.PrisonerID
    LEFT JOIN Cells C ON P.CellID = C.CellID
    WHERE M.NextCheckup BETWEEN GETDATE() AND DATEADD(DAY, @Days, GETDATE())
    ORDER BY M.NextCheckup;
END;
GO

-- =============================================
-- STORED PROCEDURES - VISITORS
-- =============================================

CREATE PROCEDURE sp_RegisterVisitor
    @FullName VARCHAR(100),
    @CNIC VARCHAR(15),
    @Phone VARCHAR(15),
    @Relationship VARCHAR(50),
    @Address VARCHAR(300)
AS
BEGIN
    SET NOCOUNT ON;
    
    IF EXISTS (SELECT 1 FROM Visitors WHERE CNIC = @CNIC)
    BEGIN
        SELECT 'CNIC already registered' AS Message, 0 AS Success;
        RETURN;
    END
    
    INSERT INTO Visitors (FullName, CNIC, Phone, Relationship, Address)
    VALUES (@FullName, @CNIC, @Phone, @Relationship, @Address);
    
    SELECT 'Visitor registered successfully' AS Message, 1 AS Success;
END;
GO

CREATE PROCEDURE sp_GetAllVisitors
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        VisitorID,
        FullName,
        CNIC,
        Phone,
        Relationship,
        Address,
        Status
    FROM Visitors
    ORDER BY FullName;
END;
GO

CREATE PROCEDURE sp_GetVisitorByCNIC
    @CNIC VARCHAR(15)
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        VisitorID,
        FullName,
        CNIC,
        Phone,
        Relationship,
        Address,
        Status
    FROM Visitors
    WHERE CNIC = @CNIC;
END;
GO

CREATE PROCEDURE sp_ScheduleVisit
    @PrisonerID INT,
    @VisitorID INT,
    @VisitDate DATE,
    @VisitTime TIME,
    @Purpose VARCHAR(200),
    @ApprovedBy VARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @PrisonerStatus VARCHAR(20);
    SELECT @PrisonerStatus = Status FROM Prisoners WHERE PrisonerID = @PrisonerID;
    
    IF @PrisonerStatus != 'Active'
    BEGIN
        SELECT 'Prisoner is not active' AS Message, 0 AS Success;
        RETURN;
    END
    
    INSERT INTO VisitorLogs (PrisonerID, VisitorID, VisitDate, VisitTime, 
                            Purpose, ApprovedBy, Status)
    VALUES (@PrisonerID, @VisitorID, @VisitDate, @VisitTime, 
            @Purpose, @ApprovedBy, 'Approved');
    
    SELECT 'Visit scheduled successfully' AS Message, 1 AS Success;
END;
GO

CREATE PROCEDURE sp_RequestVisit
    @PrisonerID INT,
    @VisitorID INT,
    @VisitDate DATE,
    @VisitTime TIME,
    @Purpose VARCHAR(200)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @PrisonerStatus VARCHAR(20);
    SELECT @PrisonerStatus = Status FROM Prisoners WHERE PrisonerID = @PrisonerID;
    
    IF @PrisonerStatus != 'Active'
    BEGIN
        SELECT 'Prisoner is not active' AS Message, 0 AS Success;
        RETURN;
    END
    
    DECLARE @VisitorStatus VARCHAR(20);
    SELECT @VisitorStatus = Status FROM Visitors WHERE VisitorID = @VisitorID;
    
    IF @VisitorStatus != 'Active'
    BEGIN
        SELECT 'Visitor is not active' AS Message, 0 AS Success;
        RETURN;
    END
    
    IF @VisitDate < CAST(GETDATE() AS DATE)
    BEGIN
        SELECT 'Visit date cannot be in the past' AS Message, 0 AS Success;
        RETURN;
    END
    
    INSERT INTO VisitorLogs (PrisonerID, VisitorID, VisitDate, VisitTime, Purpose, Status)
    VALUES (@PrisonerID, @VisitorID, @VisitDate, @VisitTime, @Purpose, 'Pending');
    
    INSERT INTO ActivityLog (Action, Description)
    VALUES ('Visit Requested', 'Visit request for Prisoner ID: ' + CAST(@PrisonerID AS VARCHAR) + 
            ' by Visitor ID: ' + CAST(@VisitorID AS VARCHAR));
    
    SELECT 'Visit request submitted successfully. Awaiting approval.' AS Message, 1 AS Success;
END;
GO

CREATE PROCEDURE sp_GetPendingVisits
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        VL.LogID,
        P.PrisonerID,
        P.FullName AS PrisonerName,
        P.CNIC AS PrisonerCNIC,
        C.CellNumber,
        C.Block,
        V.VisitorID,
        V.FullName AS VisitorName,
        V.CNIC AS VisitorCNIC,
        V.Phone AS VisitorPhone,
        V.Relationship,
        VL.VisitDate,
        VL.VisitTime,
        VL.Purpose,
        VL.Status,
        DATEDIFF(HOUR, GETDATE(), CAST(VL.VisitDate AS DATETIME) + CAST(VL.VisitTime AS DATETIME)) AS HoursUntilVisit
    FROM VisitorLogs VL
    INNER JOIN Prisoners P ON VL.PrisonerID = P.PrisonerID
    INNER JOIN Visitors V ON VL.VisitorID = V.VisitorID
    LEFT JOIN Cells C ON P.CellID = C.CellID
    WHERE VL.Status = 'Pending'
    ORDER BY VL.VisitDate, VL.VisitTime;
END;
GO

CREATE PROCEDURE sp_ApproveVisit
    @LogID INT,
    @ApprovedBy VARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    
    IF EXISTS (SELECT 1 FROM VisitorLogs WHERE LogID = @LogID AND Status = 'Pending')
    BEGIN
        UPDATE VisitorLogs
        SET Status = 'Approved', ApprovedBy = @ApprovedBy
        WHERE LogID = @LogID;
        
        INSERT INTO ActivityLog (Action, Description)
        VALUES ('Visit Approved', 'Visit LogID: ' + CAST(@LogID AS VARCHAR) + ' approved by ' + @ApprovedBy);
        
        SELECT 'Visit approved successfully' AS Message, 1 AS Success;
    END
    ELSE
    BEGIN
        SELECT 'Visit request not found or already processed' AS Message, 0 AS Success;
    END
END;
GO

CREATE PROCEDURE sp_RejectVisit
    @LogID INT,
    @RejectedBy VARCHAR(100),
    @Reason VARCHAR(500) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    IF EXISTS (SELECT 1 FROM VisitorLogs WHERE LogID = @LogID AND Status = 'Pending')
    BEGIN
        UPDATE VisitorLogs
        SET Status = 'Rejected', ApprovedBy = @RejectedBy
        WHERE LogID = @LogID;
        
        DECLARE @ReasonText VARCHAR(500);
        SET @ReasonText = ISNULL(@Reason, 'No reason provided');
        
        INSERT INTO ActivityLog (Action, Description)
        VALUES ('Visit Rejected', 'Visit LogID: ' + CAST(@LogID AS VARCHAR) + 
                ' rejected by ' + @RejectedBy + '. Reason: ' + @ReasonText);
        
        SELECT 'Visit rejected successfully' AS Message, 1 AS Success;
    END
    ELSE
    BEGIN
        SELECT 'Visit request not found or already processed' AS Message, 0 AS Success;
    END
END;
GO

CREATE PROCEDURE sp_GetAllVisitorLogs
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        VL.LogID,
        P.FullName AS PrisonerName,
        P.CNIC AS PrisonerCNIC,
        V.FullName AS VisitorName,
        V.CNIC AS VisitorCNIC,
        V.Relationship,
        VL.VisitDate,
        VL.VisitTime,
        VL.Purpose,
        VL.ApprovedBy,
        VL.Status
    FROM VisitorLogs VL
    INNER JOIN Prisoners P ON VL.PrisonerID = P.PrisonerID
    INNER JOIN Visitors V ON VL.VisitorID = V.VisitorID
    ORDER BY VL.VisitDate DESC, VL.VisitTime DESC;
END;
GO

CREATE PROCEDURE sp_GetVisitorHistory
    @VisitorID INT
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        P.FullName AS PrisonerName,
        VL.VisitDate,
        VL.VisitTime,
        VL.Purpose,
        VL.Status
    FROM VisitorLogs VL
    INNER JOIN Prisoners P ON VL.PrisonerID = P.PrisonerID
    WHERE VL.VisitorID = @VisitorID
    ORDER BY VL.VisitDate DESC;
END;
GO

CREATE PROCEDURE sp_GetVisitorLogsByDate
    @StartDate DATE,
    @EndDate DATE
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        VL.LogID,
        P.FullName AS PrisonerName,
        V.FullName AS VisitorName,
        V.Relationship,
        VL.VisitDate,
        VL.VisitTime,
        VL.Purpose,
        VL.Status
    FROM VisitorLogs VL
    INNER JOIN Prisoners P ON VL.PrisonerID = P.PrisonerID
    INNER JOIN Visitors V ON VL.VisitorID = V.VisitorID
    WHERE VL.VisitDate BETWEEN @StartDate AND @EndDate
    ORDER BY VL.VisitDate DESC;
END;
GO

CREATE PROCEDURE sp_GetVisitsByStatus
    @Status VARCHAR(20) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    IF @Status IS NULL
    BEGIN
        SELECT 
            VL.LogID,
            P.FullName AS PrisonerName,
            P.CNIC AS PrisonerCNIC,
            V.FullName AS VisitorName,
            V.CNIC AS VisitorCNIC,
            V.Relationship,
            VL.VisitDate,
            VL.VisitTime,
            VL.Purpose,
            VL.ApprovedBy,
            VL.Status
        FROM VisitorLogs VL
        INNER JOIN Prisoners P ON VL.PrisonerID = P.PrisonerID
        INNER JOIN Visitors V ON VL.VisitorID = V.VisitorID
        ORDER BY VL.VisitDate DESC, VL.VisitTime DESC;
    END
    ELSE
    BEGIN
        SELECT 
            VL.LogID,
            P.FullName AS PrisonerName,
            P.CNIC AS PrisonerCNIC,
            V.FullName AS VisitorName,
            V.CNIC AS VisitorCNIC,
            V.Relationship,
            VL.VisitDate,
            VL.VisitTime,
            VL.Purpose,
            VL.ApprovedBy,
            VL.Status
        FROM VisitorLogs VL
        INNER JOIN Prisoners P ON VL.PrisonerID = P.PrisonerID
        INNER JOIN Visitors V ON VL.VisitorID = V.VisitorID
        WHERE VL.Status = @Status
        ORDER BY VL.VisitDate DESC, VL.VisitTime DESC;
    END
END;
GO

-- =============================================
-- STORED PROCEDURES - USERS
-- =============================================

CREATE PROCEDURE sp_GetAllUsers
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        UserID,
        FullName,
        Email,
        Role,
        AssignedCell,
        Shift,
        Specialization,
        Status,
        CreatedDate,
        LastLogin
    FROM Users
    ORDER BY Role, FullName;
END;
GO

CREATE PROCEDURE sp_GetSecurityOfficers
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        UserID,
        FullName,
        Email,
        AssignedCell,
        Shift,
        Status
    FROM Users
    WHERE Role = 'Security' AND Status = 'Active'
    ORDER BY FullName;
END;
GO

CREATE PROCEDURE sp_GetAllSecurityOfficers
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        UserID AS OfficerID,
        FullName AS OfficerName,
        Shift,
        Status
    FROM Users
    WHERE Role = 'Security' AND Status = 'Active'
    ORDER BY FullName;
END;
GO

CREATE PROCEDURE sp_GetDoctors
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        UserID,
        FullName,
        Email,
        Specialization,
        Shift,
        Status
    FROM Users
    WHERE Role = 'Medical' AND Status = 'Active'
    ORDER BY FullName;
END;
GO

-- =============================================
-- STORED PROCEDURES - ACTIVITY LOG
-- =============================================

CREATE PROCEDURE sp_GetActivityLog
    @RecordCount INT = 50
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT TOP (@RecordCount)
        A.LogID,
        U.FullName AS UserName,
        U.Email,
        A.Action,
        A.Description,
        A.Timestamp
    FROM ActivityLog A
    LEFT JOIN Users U ON A.UserID = U.UserID
    ORDER BY A.Timestamp DESC;
END;
GO

-- =============================================
-- CREATE VIEWS
-- =============================================

CREATE VIEW vw_PrisonerSummary
AS
SELECT 
    P.PrisonerID,
    P.FullName,
    P.CNIC,
    P.Gender,
    P.DateOfBirth,
    P.AdmissionDate,
    P.SentenceYears,
    P.RemissionDays,
    P.ReleaseDate,
    P.Status,
    P.Crime,
    C.CellNumber,
    C.Block,
    C.CurrentOccupancy,
    C.Capacity
FROM Prisoners P
LEFT JOIN Cells C ON P.CellID = C.CellID;
GO

CREATE VIEW vw_CellOccupancy
AS
SELECT 
    CellID,
    CellNumber,
    Block,
    Capacity,
    CurrentOccupancy,
    CAST((CurrentOccupancy * 100.0 / NULLIF(Capacity,0)) AS DECIMAL(5,2)) AS OccupancyPercent,
    CASE 
        WHEN CurrentOccupancy > Capacity THEN 'Overcrowded'
        WHEN CurrentOccupancy = Capacity THEN 'Full'
        WHEN CurrentOccupancy >= (Capacity * 0.8) THEN 'High'
        ELSE 'Normal'
    END AS OccupancyStatus
FROM Cells;
GO

-- =============================================
-- DATA SEEDING
-- =============================================

-- Insert Users
INSERT INTO Users (FullName, Email, Password, Role, Shift, Status)
VALUES 
    ('Admin User', 'admin@prison.gov.pk', 'admin123', 'Admin', NULL, 'Active'),
    ('Dr. Saeed Ahmad', 'doctor@prison.gov.pk', 'doc123', 'Medical', 'Morning', 'Active'),
    ( 'Dr. Hassan Haseeb', 'doctor1@prison.gov.pk', 'doc123', 'Medical', 'Evening', 'Active'),
    ('Officer Imran Khan', 'imran@prison.gov.pk', 'sec123', 'Security', 'Morning', 'Active'),
    ('Officer Kamran Ali', 'kamran@prison.gov.pk', 'sec123', 'Security', 'Evening', 'Active'),
    ('Officer Bilal Ahmed', 'bilal@prison.gov.pk', 'sec123', 'Security', 'Night', 'Active'),
    ('Officer Hassan Raza', 'hassan@prison.gov.pk', 'sec123', 'Security', 'Morning', 'Active'),
    ('Officer Usman Tariq', 'usman@prison.gov.pk', 'sec123', 'Security', 'Evening', 'Active'),
    ('Officer Shahid Malik', 'shahid@prison.gov.pk', 'sec123', 'Security', 'Night', 'Active'),
    ('Officer Zahid Abbas', 'zahid@prison.gov.pk', 'sec123', 'Security', 'Morning', 'Active'),
    ('Officer Faisal Sheikh', 'faisal@prison.gov.pk', 'sec123', 'Security', 'Evening', 'Active'),
    ('Visitor User', 'visitor@example.com', 'vis123', 'Visitor', NULL, 'Active')
-- Insert Cells WITH Assigned Officers
INSERT INTO Cells (CellNumber, Capacity, Block, AssignedOfficer)
VALUES 
    ('A-101', 4, 'A', 'Officer Hassan Raza'),
    ('A-102', 4, 'A', 'Officer Imran Khan'),
    ('A-103', 6, 'A', 'Officer Kamran Ali'),
    ('B-201', 8, 'B', 'Officer Bilal Ahmed'),
    ('B-202', 8, 'B', 'Officer Usman Tariq'),
    ('C-301', 10, 'C', 'Officer Shahid Malik'),
    ('C-302', 10, 'C', 'Officer Zahid Abbas');

-- Insert Prisoners
INSERT INTO Prisoners (FullName, CNIC, DateOfBirth, Gender, CellID, AdmissionDate, SentenceYears, RemissionDays, Crime, Address, EmergencyContact)
VALUES 
    ('Ahmed Khan', '35202-1234567-1', '1985-03-15', 'Male', 1, '2020-01-10', 5, 30, 'Theft', 'House 123, Street 5, Lahore', '0300-1111111'),
    ('Ali Raza', '35202-2345678-2', '1990-07-22', 'Male', 1, '2021-06-15', 3, 15, 'Fraud', 'House 456, Street 8, Karachi', '0301-2222222'),
    ('Hassan Shah', '35202-3456789-3', '1988-11-30', 'Male', 2, '2019-09-20', 7, 60, 'Robbery', 'House 789, Street 12, Islamabad', '0302-3333333'),
    ('Bilal Ahmed', '35202-4567890-4', '1992-05-18', 'Male', 3, '2022-03-12', 4, 20, 'Assault', 'House 321, Street 15, Faisalabad', '0303-4444444'),
    ('Usman Malik', '35202-5678901-5', '1987-08-25', 'Male', 4, '2018-12-05', 10, 90, 'Murder', 'House 654, Street 20, Multan', '0304-5555555'),
    ('Farhan Ali', '35202-6789012-6', '1995-02-14', 'Male', 4, '2023-01-20', 2, 0, 'Drug Possession', 'House 987, Street 25, Rawalpindi', '0305-6666666'),
    ('Imran Abbas', '35202-7890123-7', '1993-09-10', 'Male', 5, '2023-06-15', 3, 10, 'Burglary', 'House 147, Street 30, Sialkot', '0306-7777777'),
    ('Kamran Aziz', '35202-8901234-8', '1989-12-05', 'Male', 6, '2022-11-20', 5, 25, 'Kidnapping', 'House 258, Street 35, Gujranwala', '0307-8888888');

-- Insert Medical Records
INSERT INTO MedicalRecords (PrisonerID, Diagnosis, Medication, DoctorName, CheckupDate, NextCheckup, Notes)
VALUES 
    (1, 'Hypertension', 'Amlodipine 5mg', 'Dr. Saeed Ahmad', '2024-12-15', '2025-01-15', 'Blood pressure stable'),
    (2, 'Diabetes Type 2', 'Metformin 500mg', 'Dr. Fatima Khan', '2024-12-20', '2025-01-20', 'Monitor blood sugar levels'),
    (3, 'Asthma', 'Salbutamol Inhaler', 'Dr. Saeed Ahmad', '2024-12-10', '2025-01-10', 'Keep inhaler accessible'),
    (5, 'Depression', 'Sertraline 50mg', 'Dr. Ayesha Siddiqui', '2024-12-25', '2025-01-25', 'Weekly counseling recommended'),
    (6, 'Migraine', 'Sumatriptan 50mg', 'Dr. Fatima Khan', '2024-12-28', '2025-01-28', 'Avoid bright lights'),
    (7, 'Back Pain', 'Ibuprofen 400mg', 'Dr. Saeed Ahmad', '2024-12-30', '2025-02-01', 'Physical therapy scheduled');

-- Insert Visitors
INSERT INTO Visitors (FullName, CNIC, Phone, Relationship, Address)
VALUES 
    ('Ayesha Khan', '35202-1111111-1', '0300-1234567', 'Wife', 'House 123, Street 5, Lahore'),
    ('Fatima Raza', '35202-2222222-2', '0301-2345678', 'Sister', 'House 456, Street 8, Karachi'),
    ('Zainab Shah', '35202-3333333-3', '0302-3456789', 'Mother', 'House 789, Street 12, Islamabad'),
    ('Amina Ahmed', '35202-4444444-4', '0303-4567890', 'Wife', 'House 321, Street 15, Faisalabad'),
    ('Saira Malik', '35202-5555555-5', '0304-5678901', 'Sister', 'House 654, Street 20, Multan'),
    ('Hina Ali', '35202-6666666-6', '0305-6789012', 'Mother', 'House 987, Street 25, Rawalpindi');

-- Insert Visitor Logs
INSERT INTO VisitorLogs (PrisonerID, VisitorID, VisitDate, VisitTime, Purpose, ApprovedBy, Status)
VALUES 
    (1, 1, '2024-12-20', '10:00:00', 'Family Visit', 'Officer Imran', 'Completed'),
    (2, 2, '2024-12-22', '14:00:00', 'Family Visit', 'Officer Kamran', 'Completed'),
    (3, 3, '2024-12-25', '11:00:00', 'Family Visit', 'Officer Imran', 'Completed'),
    (1, 1, '2024-12-28', '15:00:00', 'Family Visit', 'Officer Kamran', 'Completed'),
    (4, 4, '2024-12-29', '10:30:00', 'Family Visit', 'Officer Imran', 'Approved'),
    (5, 5, '2025-01-02', '13:00:00', 'Family Visit', 'Officer Kamran', 'Pending'),
    (6, 6, '2025-01-03', '14:30:00', 'Family Visit', 'Officer Imran', 'Pending');

GO

