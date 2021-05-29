create table User
(
	id int auto_increment,
	username varchar(255) null,
	password varchar(60) null,
	role enum('admin', 'insuranceWorker', 'doctor', 'patient') null,
	Full_name varchar(255) null,
	Date_of_birth date null,
	Function varchar(255) null,
	is_active tinyint default 1 not null,
	is_deleted tinyint default 0 not null,
	constraint id
		unique (id)
) CHARACTER SET utf8 COLLATE utf8_general_ci;

alter table User
	add primary key (id);

create table Health_problem
(
	id int auto_increment,
	Name varchar(100) not null,
	Description varchar(300) null,
	patient_id int not null,
	state enum('new', 'ongoing', 'waiting', 'closed') default 'new' not null,
	doctor_id int not null,
	constraint id
		unique (id),
	constraint Health_problem_user_id_fk
		foreign key (doctor_id) references User (id)
			on update cascade on delete cascade,
	constraint fk_Health_problem_User1
		foreign key (patient_id) references User (id)
) CHARACTER SET utf8 COLLATE utf8_general_ci;

create index fk_Health_problem_User1_idx
	on Health_problem (patient_id);

alter table Health_problem
	add primary key (id);

create table Examination_request
(
	id int auto_increment,
	State enum('waiting', 'in_progress', 'closed') default 'waiting' null,
	Text varchar(300) null,
	DateTime datetime null,
	health_problem_id int not null,
	doctor_id int null,
	constraint id
		unique (id),
	constraint fk_Examination_request_Health_problem1
		foreign key (health_problem_id) references Health_problem (id)
			on update cascade on delete cascade,
	constraint fk_Examination_request_User1
		foreign key (doctor_id) references User (id)
			on update set null on delete set null
) CHARACTER SET utf8 COLLATE utf8_general_ci;

create index fk_Examination_request_Health_problem1_idx
	on Examination_request (health_problem_id);

create index fk_Examination_request_User1_idx
	on Examination_request (doctor_id);

alter table Examination_request
	add primary key (id);

create table Health_report
(
	id int auto_increment,
	Subject varchar(50) not null,
	Text varchar(1000) not null,
	Picture longblob null,
	DateTime datetime null,
	health_problem_id int not null,
	doctor_id int null,
	examination_id int null,
	constraint id
		unique (id),
	constraint Health_report_Examination_request_id_fk
		foreign key (examination_id) references Examination_request (id)
			on update cascade on delete cascade,
	constraint fk_Health_report_Health_problem1
		foreign key (health_problem_id) references Health_problem (id)
			on update cascade on delete cascade,
	constraint fk_Health_report_user_id
		foreign key (doctor_id) references User (id)
			on update set null on delete set null
) CHARACTER SET utf8 COLLATE utf8_general_ci;

create index fk_Health_report_Health_problem1_idx
	on Health_report (health_problem_id);

create index fk_Health_report_user_id_idx
	on Health_report (doctor_id);

alter table Health_report
	add primary key (id);

create table `procedure`
(
	id int auto_increment,
	name varchar(255) not null,
	price int not null,
	constraint procedure_id_uindex
		unique (id)
) CHARACTER SET utf8 COLLATE utf8_general_ci;

alter table `procedure`
	add primary key (id);

create table procedure_payment_request
(
	id int auto_increment,
	doctor_id int not null,
	examination_id int not null,
	procedure_id int not null,
	state enum('requested', 'accepted', 'rejected') default 'requested' not null,
	constraint procedure_payment_request_id_uindex
		unique (id),
	constraint procedure_payment_request_Examination_request_id_fk
		foreign key (examination_id) references Examination_request (id)
			on update cascade on delete cascade,
	constraint procedure_payment_request_User_id_fk
		foreign key (doctor_id) references User (id)
			on update cascade on delete cascade,
	constraint procedure_payment_request_procedure_id_fk
		foreign key (procedure_id) references `procedure` (id)
) CHARACTER SET utf8 COLLATE utf8_general_ci;

alter table procedure_payment_request
	add primary key (id);

