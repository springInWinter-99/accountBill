-- 用户账单管理系统数据库表结构

-- 用户表
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
  `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
  `email` VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱',
  `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX `idx_username` (`username`),
  INDEX `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 账单表
CREATE TABLE IF NOT EXISTS `bills` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '账单ID',
  `user_id` INT NOT NULL COMMENT '用户ID',
  `title` VARCHAR(200) NOT NULL COMMENT '账单标题',
  `amount` DECIMAL(10, 2) NOT NULL COMMENT '金额',
  `category` VARCHAR(50) NOT NULL COMMENT '分类（收入/支出）',
  `type` VARCHAR(50) NOT NULL COMMENT '类型（如：餐饮、交通、工资等）',
  `description` TEXT COMMENT '描述',
  `bill_date` DATE NOT NULL COMMENT '账单日期',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_bill_date` (`bill_date`),
  INDEX `idx_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='账单表';
