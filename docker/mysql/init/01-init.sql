ALTER DATABASE `db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `user` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`role` ENUM('CLIENT', 'TRAINER', 'GYM_ADMIN', 'SUPER_ADMIN') NOT NULL,
	`first_name` VARCHAR(255) NOT NULL,
	`last_name` VARCHAR(255) NOT NULL,
	`patronymic` VARCHAR(255),
	`email` VARCHAR(255) NOT NULL UNIQUE,
	`password` VARCHAR(255) NOT NULL,
	`birth_date` DATE,
	`created_at` DATETIME NOT NULL,
	`blocked_at` DATETIME, -- если пользователя заблокирует суперадмин, то сохранится время и причина блокировки
	`blocked_comment` VARCHAR(255),
	`deleted_at` DATETIME,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `gym_blocking` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`user_id` VARCHAR(36) NOT NULL,
	`gym_id` VARCHAR(36) NOT NULL,
	`created_at` DATETIME NOT NULL,
	`comment` VARCHAR(255),
	PRIMARY KEY(`id`)
) COMMENT='блокировка пользователя администратором зала';




CREATE TABLE IF NOT EXISTS `avatar` (
	`user_id` VARCHAR(36) NOT NULL UNIQUE,
	`link` VARCHAR(255) NOT NULL,
	PRIMARY KEY(`user_id`)
) COMMENT='для пользователя нет смысла сохранять больше одной аватарки?! поэтому берем user_id = avatar_id';


CREATE TABLE IF NOT EXISTS `trainer` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`user_id` VARCHAR(36) NOT NULL,
	`gym_id` VARCHAR(36) NOT NULL,
	`phone` VARCHAR(255) NOT NULL,
	`description` VARCHAR(255) NOT NULL,
	`password` VARCHAR(255) NOT NULL, -- у тренера хранится нехэшированный пароль, чтобы администратор зала мог его смотреть и менять
	PRIMARY KEY(`id`)
) COMMENT='если пользователь имеет роль TRAINER, до для него дополнительно сохраняется эта информация';


CREATE TABLE IF NOT EXISTS `trainer_slot` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`trainer_id` VARCHAR(36) NOT NULL,
	`start_time` DATETIME NOT NULL,
	`end_time` DATETIME NOT NULL,
	`created_at` DATETIME NOT NULL,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `booking` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`user_id` VARCHAR(36) NOT NULL,
	`trainer_slot_id` VARCHAR(36) NOT NULL,
	`user_trainer_package_id` VARCHAR(36) NOT NULL,
	`status` ENUM('CREATED','CANCELLED','VISITED','NOT_VISITED') NOT NULL,
	`created_at` DATETIME NOT NULL,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `trainer_review` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`user_id` VARCHAR(36) NOT NULL,
	`trainer_id` VARCHAR(36) NOT NULL,
	`rating` TINYINT NOT NULL,
	`comment` VARCHAR(255),
	`created_at` DATETIME NOT NULL,
	`deleted_at` DATETIME,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `gym_review` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`user_id` VARCHAR(36) NOT NULL,
	`gym_id` VARCHAR(36) NOT NULL,
	`rating` TINYINT NOT NULL,
	`comment` VARCHAR(255),
	`created_at` DATETIME NOT NULL,
	`deleted_at` DATETIME,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `gym_application` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`title` VARCHAR(255) NOT NULL,
	`address` VARCHAR(255) NOT NULL,
	`description` VARCHAR(255),
	`phone` VARCHAR(255) NOT NULL,
	`status` ENUM('APPROVED', 'REJECTED', 'ON_MODERATION') NOT NULL,
	`comment` VARCHAR(255), -- комментарий от суперадмина если он отклоняет заявку или блокирует зал
	`created_at` DATETIME NOT NULL,
	`gym_admin_id` VARCHAR(36) NOT NULL,
	PRIMARY KEY(`id`)
) COMMENT='привязана к пользователю с ролью gym_admin';


CREATE TABLE IF NOT EXISTS `gym` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`gym_application_id` VARCHAR(36) NOT NULL, -- вся информация о зале берется из принятой заявки
	`created_at` DATETIME NOT NULL,
	`status` ENUM('ACTIVE', 'BLOCKED') NOT NULL, -- переходит в статус BLOCKED если суперадмин лично заблокировал зал
	PRIMARY KEY(`id`)
) COMMENT='зал создается только когда заявка принята и вся инфа о зале берется из самой заявки (поэтому зал привязан к заявке)';


CREATE TABLE IF NOT EXISTS `membership_type` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`gym_id` VARCHAR(36) NOT NULL,
	`name` VARCHAR(255) NOT NULL,
	`description` VARCHAR(255) NOT NULL,
	`price` DECIMAL(10,2) NOT NULL,
	`duration_months` INT NOT NULL,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `client_membership` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`user_id` VARCHAR(36) NOT NULL,
	`membership_type_id` VARCHAR(36) NOT NULL,
	`status` ENUM('PURCHASED', 'ACTIVE', 'EXPIRED') NOT NULL,
    `purchased_at` DATE NOT NULL,
    `activated_at` DATE,
    `expires_at` DATE,
	PRIMARY KEY(`id`)
);


CREATE TABLE trainer_package (
    `id` VARCHAR(36) PRIMARY KEY,
    `trainer_id` VARCHAR(36) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `session_count` INT NOT NULL,
    `price` DECIMAL(10,2) NOT NULL,
    `description` VARCHAR(255)
);


CREATE TABLE user_trainer_package (
    `id` VARCHAR(36) PRIMARY KEY,
    `user_id` VARCHAR(36) NOT NULL,
    `trainer_package_id` VARCHAR(36) NOT NULL,
    `status` ENUM('PURCHASED', 'ACTIVE', 'FINISHED') NOT NULL,
    `sessions_left` INT NOT NULL,
    `purchased_at` DATE NOT NULL,
    `activated_at` DATE,
    `expires_at` DATE
);


CREATE TABLE IF NOT EXISTS `gym_photo` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`gym_id` VARCHAR(36) NOT NULL,
	`link` VARCHAR(255) NOT NULL,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `gym_schedule` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`gym_id` VARCHAR(36) NOT NULL,
	`day_of_week` TINYINT NOT NULL,
	`open_time` TIME,
	`close_time` TIME,
	PRIMARY KEY(`id`)
) COMMENT='если open_time и close_time null, то зал не работает в этот день';


CREATE TABLE IF NOT EXISTS `client_progress` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`user_id` VARCHAR(36) NOT NULL,
	`weight` DECIMAL(5,2) NOT NULL,
	`height` DECIMAL(5,2) NOT NULL,
	`bmi` DECIMAL(5,2) NOT NULL,
	`recorded_at` DATETIME NOT NULL,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `subscribtion_text` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`description` TEXT NOT NULL,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `platform_subscriptions` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`value` VARCHAR(255) NOT NULL UNIQUE,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `gym_subscription` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`gym_id` VARCHAR(36) NOT NULL,
	`start_date` DATE NOT NULL,
	`end_date` DATE NOT NULL,
	PRIMARY KEY(`id`)
);


ALTER TABLE `avatar`
ADD FOREIGN KEY(`user_id`) REFERENCES `user`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `trainer`
ADD FOREIGN KEY(`user_id`) REFERENCES `user`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `gym`
ADD FOREIGN KEY(`gym_application_id`) REFERENCES `gym_application`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `trainer`
ADD FOREIGN KEY(`gym_id`) REFERENCES `gym`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `gym_photo`
ADD FOREIGN KEY(`gym_id`) REFERENCES `gym`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `gym_schedule`
ADD FOREIGN KEY(`gym_id`) REFERENCES `gym`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `gym_application`
ADD FOREIGN KEY(`gym_admin_id`) REFERENCES `user`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE `membership_type`
ADD FOREIGN KEY(`gym_id`) REFERENCES `gym`(`id`);
ALTER TABLE `client_membership`
ADD FOREIGN KEY(`user_id`) REFERENCES `user`(`id`);
ALTER TABLE `client_membership`
ADD FOREIGN KEY(`membership_type_id`) REFERENCES `membership_type`(`id`);
ALTER TABLE `trainer_package`
ADD FOREIGN KEY(`trainer_id`) REFERENCES `trainer`(`id`);
ALTER TABLE `user_trainer_package`
ADD FOREIGN KEY(`trainer_package_id`) REFERENCES `trainer_package`(`id`);
ALTER TABLE `user_trainer_package`
ADD FOREIGN KEY(`user_id`) REFERENCES `user`(`id`);

ALTER TABLE `trainer_slot`
ADD FOREIGN KEY(`trainer_id`) REFERENCES `trainer`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE `booking`
ADD FOREIGN KEY(`user_id`) REFERENCES `user`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `booking`
ADD FOREIGN KEY(`trainer_slot_id`) REFERENCES `trainer_slot`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `booking`
ADD FOREIGN KEY(`user_trainer_package_id`) REFERENCES `user_trainer_package`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE `trainer_review`
ADD FOREIGN KEY(`user_id`) REFERENCES `user`(`id`);
ALTER TABLE `trainer_review`
ADD FOREIGN KEY(`trainer_id`) REFERENCES `trainer`(`id`);
ALTER TABLE `gym_review`
ADD FOREIGN KEY(`user_id`) REFERENCES `gym`(`id`);
ALTER TABLE `gym_review`
ADD FOREIGN KEY(`gym_id`) REFERENCES `gym`(`id`);

ALTER TABLE `client_progress`
ADD FOREIGN KEY(`user_id`) REFERENCES `user`(`id`);

ALTER TABLE `gym_subscription`
ADD FOREIGN KEY(`gym_id`) REFERENCES `gym`(`id`);

ALTER TABLE `gym_blocking`
ADD FOREIGN KEY(`gym_id`) REFERENCES `gym`(`id`);
ALTER TABLE `gym_blocking`
ADD FOREIGN KEY(`user_id`) REFERENCES `user`(`id`);



INSERT INTO `user` (`id`, `role`, `first_name`, `last_name`, `email`, `password`, `created_at`)
VALUES (
    '11111111-1111-1111-1111-111111111111',
    'SUPER_ADMIN',
    'Super',
    'Admin',
    'admin@example.com',
    '$2b$12$oTc6Q2sCuJLu0VtqtCL/buMPUDfJiCIqpKYqCmvv/NdjOoVvOKIx2', -- password: Admin123!
    NOW()
) ON DUPLICATE KEY UPDATE email=email;


-- Тестовые данные


INSERT INTO `user` (`id`, `role`, `first_name`, `last_name`, `email`, `password`, `created_at`)
VALUES (
    '22222222-2222-2222-2222-222222222222',
    'GYM_ADMIN',
    'Gym',
    'Admin',
    'gym@example.com',
    '$2b$12$AXk9hO2d2jDbZA.3H7iUvugHLLo2YDPbilRGLl0EjAuqDN2GW3Nt6', -- password: password
    NOW()
) ON DUPLICATE KEY UPDATE email=email;

INSERT INTO `gym_application` (`id`, `title`, `address`, `description`, `phone`, `status`, `comment`, `created_at`, `gym_admin_id`)
VALUES ('11111111-1111-1111-1111-111111111101', 'Фитнес-центр "Атлант"', 'ул. Ленина, 15, Москва', 'Современный тренажерный зал с кардио-зоной и свободными весами', '+7 (495) 123-45-67', 'APPROVED', NULL, NOW(), '22222222-2222-2222-2222-222222222222');
INSERT INTO `gym` (`id`, `gym_application_id`, `created_at`, `status`)
VALUES ('22222222-2222-2222-2222-222222222202', '11111111-1111-1111-1111-111111111101', NOW(), 'ACTIVE');
