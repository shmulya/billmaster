CREATE TABLE `2021-08` (`date` DATE, `food` DEC(8,2) DEFAULT 0, `transp` DEC(8,2) DEFAULT 0, `health` DEC(8,2) DEFAULT 0, `home` DEC(8,2) DEFAULT 0, `smoke` DEC(8,2) DEFAULT 0, `cat` DEC(8,2) DEFAULT 0, `other` DEC(8,2) DEFAULT 0, `alco` DEC(8,2) DEFAULT 0, `etc` DEC(8,2) DEFAULT 0) engine MyISAM;
CREATE TABLE `2021-08_money` (`available` DEC(8,2), `mandatory` DEC(7,2)) engine MyISAM;
CREATE TABLE `2021-08_money_box` (`balance` DEC(7,2)) ENGINE=MyISAM;
