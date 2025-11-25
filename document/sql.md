## DDL

````SQL
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(32) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `display_name` varchar(32) DEFAULT NULL,
  `phone` varchar(32) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `cancelled` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  KEY `idx_phone` (`phone`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `friend_requests` (
  `sender_id` int NOT NULL,
  `receiver_id` int NOT NULL,
  `status` enum('pending','accepted','rejected') NOT NULL DEFAULT 'pending',
  `message` varchar(255) NOT NULL,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`sender_id`,`receiver_id`),
  KEY `idx_receiver` (`receiver_id`),
  CONSTRAINT `friend_requests_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `friend_requests_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `friends` (
  `user1_id` int NOT NULL,
  `user2_id` int NOT NULL,
  `conversation_id` int NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user1_id`,`user2_id`),
  UNIQUE KEY `conversation_id` (`conversation_id`),
  KEY `fk_friend_user2` (`user2_id`),
  CONSTRAINT `friends_ibfk_1` FOREIGN KEY (`user1_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `friends_ibfk_2` FOREIGN KEY (`user2_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `friends_ibfk_3` FOREIGN KEY (`conversation_id`) REFERENCES `conversations` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `blocks` (
  `blocker_id` int NOT NULL,
  `blocked_id` int NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`blocker_id`,`blocked_id`),
  KEY `fk_block_to` (`blocked_id`),
  CONSTRAINT `blocks_ibfk_1` FOREIGN KEY (`blocker_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `blocks_ibfk_2` FOREIGN KEY (`blocked_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `conversations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` enum('private','group') NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_conversation_type` (`type`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sender_id` int NOT NULL,
  `conversation_id` int NOT NULL,
  `content` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_msg_sender` (`sender_id`),
  KEY `fk_msg_cv` (`conversation_id`),
  KEY `idx_msg_date` (`created_at`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`conversation_id`) REFERENCES `conversations` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `chatgroups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `conversation_id` int NOT NULL,
  `owner_id` int NOT NULL,
  `group_name` varchar(32) NOT NULL,
  `number_of_members` int NOT NULL DEFAULT '0',
  `limitation` tinyint unsigned NOT NULL DEFAULT '20',
  `allow_new_member` tinyint NOT NULL DEFAULT '1',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `conversation_id` (`conversation_id`),
  KEY `fk_group_owner` (`owner_id`),
  KEY `idx_group_name` (`group_name`),
  CONSTRAINT `chatgroups_ibfk_1` FOREIGN KEY (`conversation_id`) REFERENCES `conversations` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chatgroups_ibfk_2` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

CREATE TABLE `group_members` (
  `group_id` int NOT NULL,
  `uid` int NOT NULL,
  `nickname` varchar(32) DEFAULT NULL,
  `permission` tinyint NOT NULL DEFAULT '1',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`group_id`,`uid`),
  KEY `fk_member_user` (`uid`),
  CONSTRAINT `group_members_ibfk_1` FOREIGN KEY (`group_id`) REFERENCES `chatgroups` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `group_members_ibfk_2` FOREIGN KEY (`uid`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

create definer = u23373414@`%` trigger close_conversation_delete_friend
    after delete
    on friends
    for each row
begin
        update conversations set is_active=0 where id=old.conversation_id;
    end;


create definer = u23373414@`%` trigger keep_friend_id_order
    before insert
    on friends
    for each row
begin
    declare temp int;
    if NEW.user2_id < NEW.user1_id then
        set temp = new.user2_id;
        set new.user2_id = new.user1_id;
        set new.user1_id = temp;
    end if;
end;


create definer = u23373414@`%` trigger close_conversation_delete_group
    after delete
    on chatgroups
    for each row
begin
    update conversations cv set is_active=0 where cv.id=OLD.conversation_id;
end;


create definer = u23373414@`%` trigger modify_group_member_cnt_delete
    after delete
    on group_members
    for each row
begin
    update chatgroups set number_of_members=number_of_members-1 where id=old.group_id;
end;


create definer = u23373414@`%` trigger modify_group_member_cnt_insert
    before insert
    on group_members
    for each row
begin
    if exists(select 1 from chatgroups where id=NEW.group_id and number_of_members>=limitation for update) then
        signal sqlstate '45000'
            set MESSAGE_TEXT='group is full';
    end if;
    update chatgroups set number_of_members=number_of_members+1 where id=new.group_id;
end;


````

## Procedures
````SQL
create
    definer = u23373414@`%` function areFriends(p_user1 int, p_user2 int) returns tinyint(1) deterministic
begin
    if exists(select 1
              from friends
                       join conversations on friends.conversation_id = conversations.id
              where ((user1_id = p_user1 and user2_id = p_user2)
                  or (user1_id = p_user2 and user2_id = p_user1))
                and conversations.is_active) then
        return 1;
    else
        return 0;
    end if;
end;

create
    definer = u23373414@`%` function checkMemberPermission(p_user int, p_group int, p_min_permission int) returns tinyint
    deterministic
begin
    declare v_per tinyint;
    select permission into v_per from group_members
        where uid=p_user and group_id=p_group;
    if isnull(v_per) or v_per < p_min_permission then
        return 0;
    end if;
    return 1;
end;


create
    definer = u23373414@`%` function getGroupId(p_conversation_id int) returns int deterministic
begin
    declare res int;
    select id into res from chatgroups where conversation_id=p_conversation_id;
    return res;
end;

create
    definer = u23373414@`%` function isConversationMember(p_uid int, p_cid int) returns tinyint deterministic
begin
    declare v_ctype char(10);
    select type into v_ctype from conversations where id = p_cid;
    if isnull(v_ctype) then
        return 0;
    end if;
    if v_ctype = 'private' then
        if exists(select 1 from friends where conversation_id = p_cid and (user1_id = p_uid or user2_id = p_uid)) then
            return 1;
        end if;
        return 0;
    end if;
    if v_ctype = 'group' then
        if exists(select 1
                  from group_members gm inner join chatgroups g on gm.group_id = g.id
                  where gm.uid = p_uid and g.conversation_id = p_cid) then
            return 1;
        end if;
    end if;
    return 0;
end;

create
    definer = u23373414@`%` procedure proc_register_user_base(IN p_username varchar(32),
                                                              IN p_password_hash varchar(255), OUT p_userid int,
                                                              OUT p_err_code int, OUT p_err_msg varchar(255))
begin
    declare v_cnt int;
    declare cond_err condition for sqlstate '45000';
    declare exit handler for sqlexception
        begin
            rollback;
            set p_userid = null;
            set p_err_code = 500;
            set p_err_msg = 'sql exception';
        end;

    declare exit handler for cond_err
        begin
            rollback;
            set p_userid = null;
        end;

    start transaction ;

    select count(*) into v_cnt from users where username = p_username;
    if v_cnt > 0 then
        set p_err_code = 1;
        set p_err_msg = 'user exists';
        signal cond_err;
    end if;

    insert into users (username, password_hash)
    values (p_username, p_password_hash);
    set p_userid = last_insert_id();
    set p_err_code = 0;
    set p_err_msg = 'succeed';
    commit ;
end;

create
    definer = u23373414@`%` procedure proc_alter_user_info(IN p_uid int, IN p_password varchar(255),
                                                           IN p_phone varchar(32), IN p_display_name varchar(32),
                                                           OUT p_err_code int, OUT p_err_msg varchar(255))
begin
    declare v_cnt int;
    declare cond_err condition for sqlstate '45000';
    declare exit handler for sqlexception
        begin
            rollback;
            set p_err_code = 500;
            set p_err_msg = 'sql exception';
        end;

    declare exit handler for cond_err
        begin
            rollback;
        end;

    start transaction ;
    select count(*) into v_cnt from users where id = p_uid;
    if v_cnt = 0 then
        set p_err_code = 1;
        set p_err_msg = 'user not exists';
        signal cond_err;
    end if;

    if isnull(p_phone) or isnull(p_display_name) or isnull(p_password) then
        set p_err_code = 2;
        set p_err_msg = 'null element';
        signal cond_err;
    end if;

    update users set phone = p_phone, display_name = p_display_name, password_hash = p_password
    where id = p_uid;
    set p_err_code = 0;
    set p_err_msg = 'succeed';
    commit ;
end;



create
    definer = u23373414@`%` procedure proc_send_friend_req(IN p_sender int, IN p_receiver int, IN p_msg varchar(255),
                                                           OUT p_err_code int, OUT p_err_msg varchar(255))
begin
    declare v_status char(10);
    declare cond_err condition for sqlstate '45000';
    declare exit handler for sqlexception
        begin
            rollback;
            set p_err_code = 500;
            set p_err_msg = 'sql exception';
        end;

    declare exit handler for cond_err
        begin
            rollback;
        end;

    start transaction ;
    if areFriends(p_sender, p_receiver) then
        set p_err_code = 1;
        set p_err_msg = 'already friends';
        signal cond_err;
    end if;

    if exists(select 1
              from blocks
              where blocker_id = p_receiver
                and blocked_id = p_sender) then
        set p_err_code = 2;
        set p_err_msg = 'blocked';
        signal cond_err;
    end if;

    if exists(select 1
              from blocks
              where blocked_id = p_receiver
                and blocker_id = p_sender) then
        set p_err_code = 3;
        set p_err_msg = 'should unblock firstly';
        signal cond_err;
    end if;

    if p_sender=p_receiver then
        set p_err_code = 4;
        set p_err_msg = 'cannot send friend request to oneself';
        signal cond_err;
    end if;

    select status
    into v_status
    from friend_requests
    where sender_id = p_sender
      and receiver_id = p_receiver;
    if v_status='pending' then
        set p_err_code = 5;
        set p_err_msg = 'request already sent';
        signal cond_err;
    elseif v_status='rejected' then
        update friend_requests set status='pending' , message=p_msg
        where sender_id=p_sender and receiver_id=p_receiver;
    elseif isnull(v_status) then
        insert into friend_requests (sender_id, receiver_id, message)
        values (p_sender, p_receiver, p_msg);
    end if;

    set p_err_code = 0;
    set p_err_msg = 'succeed';
    commit;
end;

create
    definer = u23373414@`%` procedure proc_respond_friend_req(IN p_receiver int, IN p_sender int,
                                                              IN p_response enum ('accept', 'reject'),
                                                              OUT p_err_code int, OUT p_err_msg varchar(255))
begin
    declare v_status char(10);
    declare cond_err condition for sqlstate '45000';
    declare exit handler for sqlexception
        begin
            rollback;
            set p_err_code = 500;
            set p_err_msg = 'sql exception';
        end;

    declare exit handler for cond_err
        begin
            rollback;
        end;

    start transaction ;
    select status into v_status from friend_requests
    where sender_id=p_sender and receiver_id=p_receiver;
    if isnull(v_status) or v_status != 'pending' then
        set p_err_code=1;
        set p_err_msg='no such pending request';
        signal cond_err;
    end if;

    if p_response='reject' then
        update friend_requests set status='rejected'
        where sender_id=p_sender and receiver_id=p_receiver;
    else
        update friend_requests set status='accepted'
        where sender_id=p_sender and receiver_id=p_receiver;
        update friend_requests set status='accepted'
        where sender_id=p_receiver and receiver_id=p_sender;
        insert into conversations (type) values ('private');
        insert into friends (user1_id, user2_id, conversation_id)
        values (p_sender, p_receiver, last_insert_id());
    end if;

    set p_err_code = 0;
    set p_err_msg = 'succeed';
    commit ;
end;

create
    definer = u23373414@`%` procedure proc_block(IN p_blocker int, IN p_blocked int, OUT p_err_code int,
                                                 OUT p_err_msg varchar(255))
begin
    declare cond_err condition for sqlstate '45000';
    declare exit handler for sqlexception
        begin
            rollback;
            set p_err_code = 500;
            set p_err_msg = 'sql exception';
        end;

    declare exit handler for cond_err
        begin
            rollback;
        end;

    start transaction ;
    if exists(select 1 from blocks where blocker_id=p_blocker and blocked_id=p_blocked) then
        set p_err_code = 1;
        set p_err_msg = 'already blocked';
        signal cond_err;
    end if;

    if areFriends(p_blocker, p_blocked) then
        call del_friend_without_commit(p_blocker, p_blocked);
    end if;

    insert into blocks (blocker_id, blocked_id) VALUES (p_blocker, p_blocked);
    update friend_requests set status='rejected' where sender_id=p_blocked and receiver_id=p_blocker;

    set p_err_code = 0;
    set p_err_msg = 'succeed';
    commit;
end;

create
    definer = u23373414@`%` procedure del_friend_without_commit(IN p_uid int, IN p_friend int)
begin
    delete from friends where (user1_id = p_uid and user2_id = p_friend) or (user2_id = p_uid and user1_id = p_friend);
    delete
    from friend_requests
    where (sender_id = p_uid and receiver_id = p_friend)
       or (receiver_id = p_uid and sender_id = p_friend);
end;

create
    definer = u23373414@`%` procedure proc_del_friend(IN p_uid int, IN p_friend int, OUT p_err_code int,
                                                      OUT p_err_msg varchar(255))
begin
    declare cond_err condition for sqlstate '45000';
    declare exit handler for sqlexception
        begin
            rollback;
            set p_err_code = 500;
            set p_err_msg = 'sql exception';
        end;

    declare exit handler for cond_err
        begin
            rollback;
        end;

    start transaction ;
    if not areFriends(p_uid, p_friend) then
        set p_err_code = 1;
        set p_err_msg = 'not friends';
        signal cond_err;
    end if;

    call del_friend_without_commit(p_uid, p_friend);

    set p_err_code = 0;
    set p_err_msg = 'succeed';
    commit;
end;

create
    definer = u23373414@`%` procedure proc_block(IN p_blocker int, IN p_blocked int, OUT p_err_code int,
                                                 OUT p_err_msg varchar(255))
begin
    declare cond_err condition for sqlstate '45000';
    declare exit handler for sqlexception
        begin
            rollback;
            set p_err_code = 500;
            set p_err_msg = 'sql exception';
        end;

    declare exit handler for cond_err
        begin
            rollback;
        end;

    start transaction ;
    if exists(select 1 from blocks where blocker_id=p_blocker and blocked_id=p_blocked) then
        set p_err_code = 1;
        set p_err_msg = 'already blocked';
        signal cond_err;
    end if;

    if areFriends(p_blocker, p_blocked) then
        call del_friend_without_commit(p_blocker, p_blocked);
    end if;

    insert into blocks (blocker_id, blocked_id) VALUES (p_blocker, p_blocked);
    update friend_requests set status='rejected' where sender_id=p_blocked and receiver_id=p_blocker;

    set p_err_code = 0;
    set p_err_msg = 'succeed';
    commit;
end;

create
    definer = u23373414@`%` procedure proc_send_message(IN p_uid int, IN p_conversation int, IN p_message text,
                                                        OUT p_err_code int, OUT p_err_msg varchar(255))
begin
    declare cond_err condition for sqlstate '45000';
    declare exit handler for sqlexception
        begin
            rollback;
            set p_err_code = 500;
            set p_err_msg = 'sql exception';
        end;

    declare exit handler for cond_err
        begin
            rollback;
        end;

    start transaction ;

    if not exists(select 1 from conversations where id=p_conversation and is_active=1) then
        set p_err_code = 1;
        set p_err_msg = 'conversation not exists or not active';
        signal cond_err;
    end if;

    if not isConversationMember(p_uid, p_conversation) then
        set p_err_code = 2;
        set p_err_msg = 'not conversation member';
        signal cond_err;
    end if;

    if exists(select 1 from conversations where id=p_conversation and type='group')
        and not checkMemberPermission(p_uid, getGroupId(p_conversation), 1) then
        set p_err_code = 3;
        set p_err_msg = 'permission denied';
        signal cond_err;
    end if;

    insert into messages (sender_id, conversation_id, content) values (p_uid, p_conversation, p_message);

    set p_err_code = 0;
    set p_err_msg = 'succeed';
    commit;
end;

create
    definer = u23373414@`%` procedure proc_create_group(IN p_uid int, IN p_name varchar(32), IN p_limitation tinyint,
                                                        OUT p_group_id int, OUT p_err_code int,
                                                        OUT p_err_msg varchar(255))
begin
    declare cond_err condition for sqlstate '45000';
    declare exit handler for sqlexception
        begin
            rollback;
            set p_group_id = null;
            set p_err_code = 500;
            set p_err_msg = 'sql exception';
        end;

    declare exit handler for cond_err
        begin
            rollback;
            set p_group_id = null;
        end;

    start transaction ;

    insert into conversations (type) values ('group');
    insert into chatgroups (conversation_id, owner_id, group_name, limitation)
    values (last_insert_id(), p_uid, p_name, p_limitation);
    set p_group_id = last_insert_id();
    insert into group_members (group_id, uid, permission)
    values (last_insert_id(), p_uid, 3);

    set p_err_code = 0;
    set p_err_msg = 'succeed';
    commit;
end;

create
    definer = u23373414@`%` procedure proc_invite_into_group(IN p_user int, IN p_invitee int, IN p_group int,
                                                             OUT p_err_code int, OUT p_err_msg varchar(255))
begin
    declare cond_err condition for sqlstate '45000';
    declare exit handler for sqlexception
        begin
            rollback;
            set p_err_code = 500;
            set p_err_msg = 'sql exception';
        end;

    declare exit handler for cond_err
        begin
            rollback;
        end;

    start transaction ;

    if not exists(select 1 from chatgroups where id=p_group and allow_new_member=1) then
        set p_err_code = 2;
        set p_err_msg = 'no such group or it does not allow new member';
        signal cond_err;
    end if;

    if not exists(select 1 from group_members where group_id=p_group and uid=p_user) then
        set p_err_code = 4;
        set p_err_msg = 'inviter is not in group';
        signal cond_err;
    end if;

    if exists(select 1 from group_members where group_id=p_group and uid=p_invitee) then
        set p_err_code = 5;
        set p_err_msg = 'invitee is in group';
        signal cond_err;
    end if;

    if not checkMemberPermission(p_user, p_group, 1) then
        set p_err_code = 6;
        set p_err_msg = 'permission denied';
        signal cond_err;
    end if;

    insert into group_members (group_id, uid, permission) values (p_group, p_invitee, 1);

    set p_err_code = 0;
    set p_err_msg = 'succeed';
    commit;
end;

create
    definer = u23373414@`%` procedure proc_modify_group_option(IN p_modifier int, IN p_group int, IN p_name varchar(32),
                                                               IN p_limit int, IN p_allow_new tinyint,
                                                               OUT p_err_code int, OUT p_err_msg varchar(255))
begin
    declare v_member int;
    declare cond_err condition for sqlstate '45000';
    declare exit handler for sqlexception
        begin
            rollback;
            set p_err_code = 500;
            set p_err_msg = 'sql exception';
        end;

    declare exit handler for cond_err
        begin
            rollback;
        end;

    start transaction ;

    if not checkMemberPermission(p_modifier, p_group, 2) then
        set p_err_code = 1;
        set p_err_msg = 'permission denied';
        signal cond_err;
    end if;


    select number_of_members into v_member from chatgroups where id=p_group for update ;
    if p_limit < v_member or p_limit > 200 then
        set p_err_code = 2;
        set p_err_msg = 'should no less than number of members now and no more than 200';
        signal cond_err;
    end if;

    update chatgroups set group_name=p_name, limitation=p_limit, allow_new_member=p_allow_new where id=p_group;

    set p_err_code = 0;
    set p_err_msg = 'succeed';
    commit;
end;

create
    definer = u23373414@`%` procedure proc_modify_member_permission(IN p_modifier int, IN p_member int, IN p_group int,
                                                                    IN p_permission tinyint, OUT p_err_code int,
                                                                    OUT p_err_msg varchar(255))
begin
    declare v_perm1 int;
    declare v_perm2 int;
    declare cond_err condition for sqlstate '45000';
    declare exit handler for sqlexception
        begin
            rollback;
            set p_err_code = 500;
            set p_err_msg = 'sql exception';
        end;

    declare exit handler for cond_err
        begin
            rollback;
        end;

    start transaction ;
    if p_permission < 0 then
        set p_permission = 0;
    elseif p_permission > 3 then
        set p_permission = 3;
    end if;

    if not exists(select 1 from group_members where group_id = p_group and uid = p_modifier) or
       not exists(select 1 from group_members where group_id = p_group and uid = p_member) then
        set p_err_code = 1;
        set p_err_msg = 'someone is not in group';
        signal cond_err;
    end if;

    select permission into v_perm1 from group_members where group_id = p_group and uid = p_modifier;
    select permission into v_perm2 from group_members where group_id = p_group and uid = p_member;

    if v_perm1 < 2 or v_perm2 >= v_perm1 or p_permission > v_perm1 then
        set p_err_code = 2;
        set p_err_msg = 'permission denied';
        signal cond_err;
    end if;

    update group_members set permission=p_permission where group_id = p_group and uid = p_member;
    if p_permission >= 3 then
        update group_members set permission=2 where group_id = p_group and uid = p_modifier;
        update chatgroups set owner_id=p_member where id = p_group;
    end if;

    set p_err_code = 0;
    set p_err_msg = 'succeed';
    commit;
end;

create
    definer = u23373414@`%` procedure proc_exit_group(IN p_requestor int, IN p_target int, IN p_group int,
                                                      OUT p_err_code int, OUT p_err_msg varchar(255))
begin
    declare v_perm1 int;
    declare v_perm2 int;
    declare cond_err condition for sqlstate '45000';
    declare exit handler for sqlexception
        begin
            rollback;
            set p_err_code = 500;
            set p_err_msg = 'sql exception';
        end;

    declare exit handler for cond_err
        begin
            rollback;
        end;

    start transaction ;

    select permission into v_perm1 from group_members where group_id=p_group and uid=p_requestor;
    select permission into v_perm2 from group_members where group_id=p_group and uid=p_target;

    if isnull(v_perm1) or isnull(v_perm2) then
        set p_err_code = 1;
        set p_err_msg = 'someone not in group';
        signal cond_err;
    end if;

    if p_requestor<>p_target and (v_perm1<=v_perm2 or v_perm1<2) then
        set p_err_code = 2;
        set p_err_msg = 'permission denied';
        signal cond_err;
    end if;

    if p_requestor=p_target and p_requestor=(select g.owner_id from chatgroups g where g.id=p_group) then
        set p_err_code = 3;
        set p_err_msg = 'owner should transferred before exiting group';
        signal cond_err;
    end if;

    delete from group_members where group_id=p_group and uid=p_target;

    set p_err_code = 0;
    set p_err_msg = 'succeed';
    commit;
end;

create
    definer = u23373414@`%` procedure proc_dissolve_group(IN p_requestor int, IN p_group int, OUT p_err_code int,
                                                          OUT p_err_msg varchar(255))
begin
    declare cond_err condition for sqlstate '45000';
    declare exit handler for sqlexception
        begin
            rollback;
            set p_err_code = 500;
            set p_err_msg = 'sql exception';
        end;

    declare exit handler for cond_err
        begin
            rollback;
        end;

    start transaction ;

    if not exists(select 1 from group_members where group_id=p_group and uid=p_requestor) then
        set p_err_code = 1;
        set p_err_msg = 'not group member';
        signal cond_err;
    end if;

    if p_requestor<>(
        select owner_id from chatgroups where id=p_group
        ) then
        set p_err_code = 2;
        set p_err_msg = 'permission denied';
        signal cond_err;
    end if;

    delete from chatgroups where id=p_group;

    set p_err_code = 0;
    set p_err_msg = 'succeed';
    commit;
end;


````