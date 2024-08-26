create database educursos;
use educursos;
unlock tables;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    sobrenome VARCHAR(255) NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

ALTER TABLE usuarios ADD COLUMN profile_image VARCHAR(255);

select * from usuarios;	

CREATE TABLE cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    vagas_disponiveis INT DEFAULT 20,
    vagas_totais INT DEFAULT 20
);

select * from cursos;

INSERT INTO cursos (nome, vagas_disponiveis, vagas_totais) VALUES
('Ciências de Dados', 20, 20),
('Banco de Dados', 20, 20),
('Nuvem', 20, 20),
('Design de Jogos', 20, 20);

select * from cursos;

CREATE TABLE inscricoes_cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_curso INT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id),
    FOREIGN KEY (id_curso) REFERENCES cursos(id)
);

select * from inscricoes_cursos;

SELECT u.nome AS NomeUsuario, c.nome AS NomeCurso
FROM inscricoes_cursos ic
JOIN usuarios u ON ic.id_usuario = u.id
JOIN cursos c ON ic.id_curso = c.id;

CREATE TABLE provas (
  id int NOT NULL AUTO_INCREMENT,
  id_usuario int NOT NULL,
  id_curso int NOT NULL,
  nome varchar(255) NOT NULL,
  data date DEFAULT NULL,
  nome_curso varchar(255) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY id_usuario (id_usuario),
  KEY id_curso (id_curso),
  CONSTRAINT provas_ibfk_1 FOREIGN KEY (id_usuario) REFERENCES usuarios (id),
  CONSTRAINT provas_ibfk_2 FOREIGN KEY (id_curso) REFERENCES cursos (id)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO provas VALUES (1,1,1,'Prova de exemplo','2024-06-19','Ciências de Dados');

CREATE TABLE trabalhos (
  id int NOT NULL AUTO_INCREMENT,
  id_usuario int NOT NULL,
  id_curso int NOT NULL,
  titulo varchar(255) NOT NULL,
  descricao text,
  data_entrega date NOT NULL,
  data date DEFAULT NULL,
  PRIMARY KEY (id),
  KEY id_usuario (id_usuario),
  KEY id_curso (id_curso),
  CONSTRAINT trabalhos_ibfk_1 FOREIGN KEY (id_usuario) REFERENCES usuarios (id),
  CONSTRAINT trabalhos_ibfk_2 FOREIGN KEY (id_curso) REFERENCES cursos (id)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

select * from trabalhos;
INSERT INTO trabalhos VALUES (1,1,1,'Trabalho de Exemplo','Descrição detalhada do trabalho de exemplo.','2024-06-30','2024-06-12'),(2,1,2,'av2','trabalho de av2','2024-06-08','2024-06-02');

CREATE TABLE trabenviados (
  id int NOT NULL AUTO_INCREMENT,
  id_usuario int NOT NULL,
  id_curso int NOT NULL,
  id_trabalho int NOT NULL,
  titulo varchar(255) NOT NULL,
  data_envio datetime NOT NULL,
  file_path varchar(255) NOT NULL,
  PRIMARY KEY (id),
  KEY id_usuario (id_usuario),
  KEY id_curso (id_curso),
  KEY id_trabalho (id_trabalho),
  CONSTRAINT trabenviados_ibfk_1 FOREIGN KEY (id_usuario) REFERENCES usuarios (id),
  CONSTRAINT trabenviados_ibfk_2 FOREIGN KEY (id_curso) REFERENCES cursos (id),
  CONSTRAINT trabenviados_ibfk_3 FOREIGN KEY (id_trabalho) REFERENCES trabalhos (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

