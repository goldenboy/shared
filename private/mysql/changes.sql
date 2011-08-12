CREATE TABLE IF NOT EXISTS `city` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `province_id` int(11) DEFAULT 0,
  `created_on` datetime DEFAULT NULL,
  `updated_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
CREATE TABLE IF NOT EXISTS `province` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `code` varchar(255) DEFAULT NULL,
  `country_id` int(11) DEFAULT 0,
  `created_on` datetime DEFAULT NULL,
  `updated_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
CREATE TABLE IF NOT EXISTS `country` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `code` varchar(255) DEFAULT NULL,
  `created_on` datetime DEFAULT NULL,
  `updated_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
CREATE TABLE IF NOT EXISTS `postal_code` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `city_id` int(11) DEFAULT 0,
  `latitude` decimal(10,6) DEFAULT 0,
  `longitude` decimal(10,6) DEFAULT 0,
  `created_on` datetime DEFAULT NULL,
  `updated_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
ALTER IGNORE TABLE account DROP column creation_date;
ALTER IGNORE TABLE account DROP column modified_date;
ALTER IGNORE TABLE company DROP column creation_date;
ALTER IGNORE TABLE company DROP column modified_date;
ALTER IGNORE TABLE test DROP column creation_date;
ALTER IGNORE TABLE test DROP column modified_date;
ALTER IGNORE TABLE account ADD column created_on datetime DEFAULT NULL;
ALTER IGNORE TABLE account ADD column updated_on datetime DEFAULT NULL;
ALTER IGNORE TABLE company ADD column created_on datetime DEFAULT NULL;
ALTER IGNORE TABLE company ADD column updated_on datetime DEFAULT NULL;
ALTER IGNORE TABLE setting ADD column created_on datetime DEFAULT NULL;
ALTER IGNORE TABLE setting ADD column updated_on datetime DEFAULT NULL;
ALTER IGNORE TABLE test ADD column created_on datetime DEFAULT NULL;
ALTER IGNORE TABLE test ADD column updated_on datetime DEFAULT NULL;
