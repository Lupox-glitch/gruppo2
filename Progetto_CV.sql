CREATE TABLE Utenti (
Id_Utente INT PRIMARY KEY,
Email VARCHAR(50),
PasswordM VARCHAR(50),
Nome VARCHAR(50),
Cognome VARCHAR(50),
Data_Nascita DATE,
Nazionalità VARCHAR(50)
);

CREATE TABLE CV (
Id_CV INT PRIMARY KEY,
PDF_Path_Up VARCHAR(50),
N_Telefono INT,
Email_Contatto VARCHAR(50),
Indirizzo VARCHAR(50),
Formazione VARCHAR(650),
Lingue VARCHAR(150),
Esperienza_Lavorativa VARCHAR(950),
Skill VARCHAR(250),
Hobby VARCHAR(250),
Lettera_Presentazione VARCHAR(1950),
Id_Utente_CV INT,
FOREIGN KEY (Id_Utente_CV) REFERENCES Utenti(Id_Utente)
);