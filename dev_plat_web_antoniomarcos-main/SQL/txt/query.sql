create database devplatweb;
use devplatweb;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    sobrenome VARCHAR(255) NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

select * from usuarios;

CREATE TABLE cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    vagas_disponiveis INT DEFAULT 20,
    vagas_totais INT DEFAULT 20
);

select * from cursos;

INSERT INTO cursos (nome, vagas_disponiveis, vagas_totais) VALUES
('ciencias_de_dados', 20, 20),
('banco_de_dados', 20, 20),
('nuvem', 20, 20),
('design_de_jogos', 20, 20);

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
