SET NAMES 'utf8mb4' COLLATE 'utf8mb4_unicode_ci';
SET CHARACTER SET utf8mb4;

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
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`blocked_at` DATETIME, -- если пользователя заблокирует суперадмин, то сохранится время и причина блокировки
	`blocked_comment` VARCHAR(255),
	`deleted_at` DATETIME,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `gym_blocking` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`user_id` VARCHAR(36) NOT NULL,
	`gym_id` VARCHAR(36) NOT NULL,
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
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
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`deleted_at` DATETIME,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `booking` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`user_id` VARCHAR(36) NOT NULL,
	`trainer_slot_id` VARCHAR(36) NOT NULL,
	`user_trainer_package_id` VARCHAR(36) NOT NULL,
	`status` ENUM('CREATED','CANCELLED','VISITED','NOT_VISITED') NOT NULL,
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `trainer_review` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`user_id` VARCHAR(36) NOT NULL,
	`trainer_id` VARCHAR(36) NOT NULL,
	`rating` TINYINT NOT NULL,
	`comment` VARCHAR(255),
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`deleted_at` DATETIME,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `gym_review` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`user_id` VARCHAR(36) NOT NULL,
	`gym_id` VARCHAR(36) NOT NULL,
	`rating` TINYINT NOT NULL,
	`comment` VARCHAR(255),
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
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
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`gym_admin_id` VARCHAR(36) NOT NULL,
	PRIMARY KEY(`id`)
) COMMENT='привязана к пользователю с ролью gym_admin';


CREATE TABLE IF NOT EXISTS `gym` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`gym_application_id` VARCHAR(36) NOT NULL, -- вся информация о зале берется из принятой заявки
	`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
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


CREATE TABLE IF NOT EXISTS `trainer_package` (
    `id` VARCHAR(36) NOT NULL UNIQUE,
    `trainer_id` VARCHAR(36) NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `session_count` INT NOT NULL,
    `price` DECIMAL(10,2) NOT NULL,
    `description` VARCHAR(255),
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `user_trainer_package` (
    `id` VARCHAR(36) NOT NULL UNIQUE,
    `user_id` VARCHAR(36) NOT NULL,
    `trainer_package_id` VARCHAR(36) NOT NULL,
    `status` ENUM('PURCHASED', 'ACTIVE', 'FINISHED') NOT NULL,
    `sessions_left` INT NOT NULL,
    `purchased_at` DATE NOT NULL,
    `activated_at` DATE,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `gym_photo` (
	`gym_id` VARCHAR(36) NOT NULL UNIQUE,
	`link` VARCHAR(255) NOT NULL,
	PRIMARY KEY(`gym_id`)
) COMMENT='для зала нет смысла хранить больше одной фотографии, поэтому используем gym_id как primary key';


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


CREATE TABLE IF NOT EXISTS `subscription_text` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`description` TEXT NOT NULL,
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `platform_subscriptions` (
	`id` VARCHAR(36) NOT NULL UNIQUE,
	`value` INT NOT NULL UNIQUE,
    `description` VARCHAR(255) NOT NULL,
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
ADD FOREIGN KEY(`user_id`) REFERENCES `user`(`id`);
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


INSERT INTO `platform_subscriptions` (`id`, `value`, `description`)
VALUES ('11111111-1111-1111-1111-101111111111', 1, '1 Месяц'),
('11111111-1111-1111-1111-110111111111', 3, '3 Месяца'),
('11111111-1111-1111-1111-111011111111', 12, '12 Месяцев') ON DUPLICATE KEY UPDATE value=value;

INSERT INTO `subscription_text` (`id`, `description`)
VALUES ('11111001-1111-1111-1111-101111111111', 'После отправки формы подтверждения, пожалуйста, переходите к оплате.
1. Выберите тариф:
- 1 месяц — 10 000 ₽
- 6 месяцев — 50 000 ₽
- 12 месяцев — 90 000 ₽
2. Оплатите. Для этого воспользуйтесь реквизитами ниже.
Важно: Заявка будет отклонена, если оплата не поступит в течение 24 часов.
Реквизиты для перевода:
Получатель: ИП Иванов Иван
Номер счета: 1234567890123
В обязательном порядке укажите в комментарии к переводу:
- Название зала
- Ваш номер телефона
- Выбранный вид подписки (Месяц / 6 месяцев / Год)') ON DUPLICATE KEY UPDATE description=description;


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
VALUES ('11111111-1111-1111-1111-111111111101', 'Фитнес-центр "Атлант"', 'г. Москва, ул. Ленина, 15', 'Современный тренажерный зал с кардио-зоной и свободными весами', '+7 (495) 123-45-67', 'APPROVED', NULL, NOW(), '22222222-2222-2222-2222-222222222222');
INSERT INTO `gym` (`id`, `gym_application_id`, `created_at`, `status`)
VALUES ('22222222-2222-2222-2222-222222222202', '11111111-1111-1111-1111-111111111101', NOW(), 'ACTIVE');
INSERT INTO `gym_subscription` (`id`, `gym_id`, `start_date`, `end_date`)
VALUES ('33333333-2222-2222-2222-222222222202', '22222222-2222-2222-2222-222222222202', '2026-03-21', '2027-03-21');

INSERT INTO `gym_schedule` (`id`, `gym_id`, `day_of_week`, `open_time`, `close_time`)
VALUES('33333333-3333-2222-2222-222222222201', '22222222-2222-2222-2222-222222222202', 0, '08:00:00', '21:00:00'),
('33333333-3333-2222-2222-222222222202', '22222222-2222-2222-2222-222222222202', 1, '08:00:00', '21:00:00'),
('33333333-3333-2222-2222-222222222203', '22222222-2222-2222-2222-222222222202', 2, '08:00:00', '21:00:00'),
('33333333-3333-2222-2222-222222222204', '22222222-2222-2222-2222-222222222202', 3, '08:00:00', '21:00:00'),
('33333333-3333-2222-2222-222222222205', '22222222-2222-2222-2222-222222222202', 4, '08:00:00', '21:00:00'),
('33333333-3333-2222-2222-222222222206', '22222222-2222-2222-2222-222222222202', 5, '08:00:00', '21:00:00'),
('33333333-3333-2222-2222-222222222207', '22222222-2222-2222-2222-222222222202', 6, '08:00:00', '21:00:00');

INSERT INTO `user` (`id`, `role`, `first_name`, `last_name`, `email`, `password`, `created_at`)
VALUES (
    '22222222-2222-2222-2222-222222222223',
    'GYM_ADMIN',
    'Gym',
    'Admin 2',
    'gym1@example.com',
    '$2b$12$AXk9hO2d2jDbZA.3H7iUvugHLLo2YDPbilRGLl0EjAuqDN2GW3Nt6', -- password: password
    NOW()
) ON DUPLICATE KEY UPDATE email=email;

INSERT INTO `gym_application` (`id`, `title`, `address`, `description`, `phone`, `status`, `comment`, `created_at`, `gym_admin_id`)
VALUES ('11111111-1111-1111-1111-111111111102', 'Фитнес-зал "Олимп"', 'г. Москва, ул. Тверская, 8', 'Просторный зал с силовой и функциональной зонами', '+7 (495) 234-56-78', 'APPROVED', NULL, NOW(), '22222222-2222-2222-2222-222222222223');

INSERT INTO `gym` (`id`, `gym_application_id`, `created_at`, `status`)
VALUES ('22222222-2222-2222-2222-222222222203', '11111111-1111-1111-1111-111111111102', NOW(), 'ACTIVE');

INSERT INTO `gym_subscription` (`id`, `gym_id`, `start_date`, `end_date`)
VALUES ('33333333-2222-2222-2222-222222222203', '22222222-2222-2222-2222-222222222203', '2026-03-21', '2027-03-21');

INSERT INTO `gym_schedule` (`id`, `gym_id`, `day_of_week`, `open_time`, `close_time`)
VALUES('33333333-3333-2222-2222-222222222208', '22222222-2222-2222-2222-222222222203', 0, '08:00:00', '21:00:00'),
('33333333-3333-2222-2222-222222222209', '22222222-2222-2222-2222-222222222203', 1, '08:00:00', '21:00:00'),
('33333333-3333-2222-2222-222222222210', '22222222-2222-2222-2222-222222222203', 2, '08:00:00', '21:00:00'),
('33333333-3333-2222-2222-222222222211', '22222222-2222-2222-2222-222222222203', 3, '08:00:00', '21:00:00'),
('33333333-3333-2222-2222-222222222212', '22222222-2222-2222-2222-222222222203', 4, '08:00:00', '21:00:00'),
('33333333-3333-2222-2222-222222222213', '22222222-2222-2222-2222-222222222203', 5, '08:00:00', '21:00:00'),
('33333333-3333-2222-2222-222222222214', '22222222-2222-2222-2222-222222222203', 6, '08:00:00', '21:00:00');


INSERT INTO `user` (`id`, `role`, `first_name`, `last_name`, `email`, `password`, `created_at`)
VALUES (
    '22222222-2222-2222-2222-222222222224',
    'GYM_ADMIN',
    'Elena',
    'Morozova',
    'gym.new.admin@example.com',
    '$2b$12$AXk9hO2d2jDbZA.3H7iUvugHLLo2YDPbilRGLl0EjAuqDN2GW3Nt6', -- password: password
    NOW()
) ON DUPLICATE KEY UPDATE email=email;

INSERT INTO `gym_application` (`id`, `title`, `address`, `description`, `phone`, `status`, `comment`, `created_at`, `gym_admin_id`)
VALUES (
    '11111111-1111-1111-1111-111111111103',
    'Фитнес-студия "Вектор"',
    'г. Москва, ул. Садовая, 42',
    'Небольшой зал с акцентом на функциональный тренинг и персональные занятия',
    '+7 (495) 345-67-89',
    'ON_MODERATION',
    NULL,
    NOW(),
    '22222222-2222-2222-2222-222222222224'
);

INSERT INTO `user` (`id`, `role`, `first_name`, `last_name`, `email`, `password`, `created_at`)
VALUES (
    '44444444-4444-4444-4444-444444444401',
    'TRAINER',
    'Иван',
    'Соколов',
    'trainer.ivan@example.com',
    '$2b$12$AXk9hO2d2jDbZA.3H7iUvugHLLo2YDPbilRGLl0EjAuqDN2GW3Nt6', -- password: password
    NOW()
), (
    '44444444-4444-4444-4444-444444444402',
    'TRAINER',
    'Мария',
    'Волкова',
    'trainer.maria@example.com',
    '$2b$12$AXk9hO2d2jDbZA.3H7iUvugHLLo2YDPbilRGLl0EjAuqDN2GW3Nt6', -- password: password
    NOW()
), (
    '55555555-5555-5555-5555-555555555501',
    'CLIENT',
    'Алексей',
    'Петров',
    'client.alexey@example.com',
    '$2b$12$AXk9hO2d2jDbZA.3H7iUvugHLLo2YDPbilRGLl0EjAuqDN2GW3Nt6', -- password: password
    NOW()
), (
    '55555555-5555-5555-5555-555555555502',
    'CLIENT',
    'Ольга',
    'Смирнова',
    'client.olga@example.com',
    '$2b$12$AXk9hO2d2jDbZA.3H7iUvugHLLo2YDPbilRGLl0EjAuqDN2GW3Nt6', -- password: password
    NOW()
) ON DUPLICATE KEY UPDATE email=email;

INSERT INTO `trainer` (`id`, `user_id`, `gym_id`, `phone`, `description`, `password`)
VALUES (
    '66666666-6666-6666-6666-666666666601',
    '44444444-4444-4444-4444-444444444401',
    '22222222-2222-2222-2222-222222222202',
    '+7 (901) 111-22-33',
    'Силовой тренинг и набор мышечной массы',
    'password'
), (
    '66666666-6666-6666-6666-666666666602',
    '44444444-4444-4444-4444-444444444402',
    '22222222-2222-2222-2222-222222222202',
    '+7 (902) 444-55-66',
    'Функциональный тренинг и мобильность',
    'password'
);

INSERT INTO `membership_type` (`id`, `gym_id`, `name`, `description`, `price`, `duration_months`)
VALUES (
    '77777777-7777-7777-7777-777777777701',
    '22222222-2222-2222-2222-222222222202',
    'Стандарт 1 месяц',
    'Посещение зала без персональных тренировок',
    3500.00,
    1
);

INSERT INTO `client_membership` (`id`, `user_id`, `membership_type_id`, `status`, `purchased_at`, `activated_at`, `expires_at`)
VALUES (
    '88888888-8888-8888-8888-888888888801',
    '55555555-5555-5555-5555-555555555501',
    '77777777-7777-7777-7777-777777777701',
    'ACTIVE',
    DATE_SUB(CURDATE(), INTERVAL 10 DAY),
    DATE_SUB(CURDATE(), INTERVAL 7 DAY),
    DATE_ADD(CURDATE(), INTERVAL 23 DAY)
), (
    '88888888-8888-8888-8888-888888888802',
    '55555555-5555-5555-5555-555555555502',
    '77777777-7777-7777-7777-777777777701',
    'ACTIVE',
    DATE_SUB(CURDATE(), INTERVAL 10 DAY),
    DATE_SUB(CURDATE(), INTERVAL 7 DAY),
    DATE_ADD(CURDATE(), INTERVAL 23 DAY)
);

INSERT INTO `trainer_package` (`id`, `trainer_id`, `name`, `session_count`, `price`, `description`)
VALUES (
    '99999999-9999-9999-9999-999999999901',
    '66666666-6666-6666-6666-666666666601',
    'Персональный пакет 8 занятий',
    8,
    12000.00,
    'Индивидуальные тренировки с прогресс-контролем'
);

INSERT INTO `user_trainer_package` (`id`, `user_id`, `trainer_package_id`, `status`, `sessions_left`, `purchased_at`, `activated_at`)
VALUES (
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01',
    '55555555-5555-5555-5555-555555555502',
    '99999999-9999-9999-9999-999999999901',
    'ACTIVE',
    7,
    DATE_SUB(CURDATE(), INTERVAL 5 DAY),
    DATE_SUB(CURDATE(), INTERVAL 4 DAY)
);

INSERT INTO `trainer_slot` (`id`, `trainer_id`, `start_time`, `end_time`, `created_at`, `deleted_at`)
VALUES (
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbb01',
    '66666666-6666-6666-6666-666666666601',
    DATE_SUB(NOW(), INTERVAL 3 HOUR),
    DATE_SUB(NOW(), INTERVAL 2 HOUR),
    NOW(),
    NULL
), (
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbb02',
    '66666666-6666-6666-6666-666666666601',
    DATE_ADD(NOW(), INTERVAL 2 HOUR),
    DATE_ADD(NOW(), INTERVAL 3 HOUR),
    NOW(),
    NULL
), (
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbb03',
    '66666666-6666-6666-6666-666666666601',
    DATE_ADD(NOW(), INTERVAL 4 HOUR),
    DATE_ADD(NOW(), INTERVAL 5 HOUR),
    NOW(),
    NULL
);

INSERT INTO `booking` (`id`, `user_id`, `trainer_slot_id`, `user_trainer_package_id`, `status`, `created_at`)
VALUES (
    'cccccccc-cccc-cccc-cccc-cccccccccc01',
    '55555555-5555-5555-5555-555555555502',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbb01',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01',
    'VISITED',
    NOW()
), (
    'cccccccc-cccc-cccc-cccc-cccccccccc02',
    '55555555-5555-5555-5555-555555555502',
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbb02',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01',
    'CREATED',
    NOW()
);

INSERT INTO `trainer_review` (`id`, `user_id`, `trainer_id`, `rating`, `comment`, `created_at`, `deleted_at`)
VALUES (
    'dddddddd-dddd-dddd-dddd-dddddddddd01',
    '55555555-5555-5555-5555-555555555502',
    '66666666-6666-6666-6666-666666666601',
    5,
    'Тренер очень внимательный, нагрузка подобрана отлично',
    NOW(),
    NULL
);

INSERT INTO `gym_review` (`id`, `user_id`, `gym_id`, `rating`, `comment`, `created_at`, `deleted_at`)
VALUES (
    'eeeeeeee-eeee-eeee-eeee-eeeeeeeeee01',
    '55555555-5555-5555-5555-555555555501',
    '22222222-2222-2222-2222-222222222202',
    5,
    'Чистый зал, новое оборудование, комфортная атмосфера',
    NOW(),
    NULL
);

