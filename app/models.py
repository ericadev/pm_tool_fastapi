from typing import Optional
import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Tag(Base):
    __tablename__ = 'Tag'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='Tag_pkey'),
        Index('Tag_name_idx', 'name'),
        Index('Tag_name_key', 'name', unique=True)
    )

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    createdAt: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    color: Mapped[Optional[str]] = mapped_column(Text, server_default=text("'#6366f1'::text"))

    TaskTag: Mapped[list['TaskTag']] = relationship('TaskTag', back_populates='Tag_')


class User(Base):
    __tablename__ = 'User'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='User_pkey'),
        Index('User_email_idx', 'email'),
        Index('User_email_key', 'email', unique=True)
    )

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    createdAt: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updatedAt: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), nullable=False)
    firstName: Mapped[Optional[str]] = mapped_column(Text)
    lastName: Mapped[Optional[str]] = mapped_column(Text)
    avatar: Mapped[Optional[str]] = mapped_column(Text)

    Notification: Mapped[list['Notification']] = relationship('Notification', back_populates='User_')
    Project: Mapped[list['Project']] = relationship('Project', back_populates='User_')
    ProjectMember: Mapped[list['ProjectMember']] = relationship('ProjectMember', back_populates='User_')
    Task: Mapped[list['Task']] = relationship('Task', foreign_keys='[Task.assigneeId]', back_populates='User_')
    Task_: Mapped[list['Task']] = relationship('Task', foreign_keys='[Task.creatorId]', back_populates='User1')
    Activity: Mapped[list['Activity']] = relationship('Activity', back_populates='User_')
    Comment: Mapped[list['Comment']] = relationship('Comment', back_populates='User_')


class PrismaMigrations(Base):
    __tablename__ = '_prisma_migrations'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='_prisma_migrations_pkey'),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    migration_name: Mapped[str] = mapped_column(String(255), nullable=False)
    started_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    applied_steps_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    finished_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    logs: Mapped[Optional[str]] = mapped_column(Text)
    rolled_back_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))


class Notification(Base):
    __tablename__ = 'Notification'
    __table_args__ = (
        ForeignKeyConstraint(['userId'], ['User.id'], ondelete='CASCADE', onupdate='CASCADE', name='Notification_userId_fkey'),
        PrimaryKeyConstraint('id', name='Notification_pkey'),
        Index('Notification_userId_isRead_idx', 'userId', 'isRead')
    )

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    userId: Mapped[str] = mapped_column(Text, nullable=False)
    isRead: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'))
    createdAt: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    metadata_: Mapped[Optional[dict]] = mapped_column('metadata', JSONB)

    User_: Mapped['User'] = relationship('User', back_populates='Notification')


class Project(Base):
    __tablename__ = 'Project'
    __table_args__ = (
        ForeignKeyConstraint(['ownerId'], ['User.id'], ondelete='CASCADE', onupdate='CASCADE', name='Project_ownerId_fkey'),
        PrimaryKeyConstraint('id', name='Project_pkey'),
        Index('Project_ownerId_idx', 'ownerId')
    )

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    ownerId: Mapped[str] = mapped_column(Text, nullable=False)
    createdAt: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updatedAt: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    color: Mapped[Optional[str]] = mapped_column(Text, server_default=text("'#3b82f6'::text"))
    icon: Mapped[Optional[str]] = mapped_column(Text, server_default=text("'folder'::text"))

    User_: Mapped['User'] = relationship('User', back_populates='Project')
    ProjectMember: Mapped[list['ProjectMember']] = relationship('ProjectMember', back_populates='Project_')
    Task: Mapped[list['Task']] = relationship('Task', back_populates='Project_')
    Activity: Mapped[list['Activity']] = relationship('Activity', back_populates='Project_')


class ProjectMember(Base):
    __tablename__ = 'ProjectMember'
    __table_args__ = (
        ForeignKeyConstraint(['projectId'], ['Project.id'], ondelete='CASCADE', onupdate='CASCADE', name='ProjectMember_projectId_fkey'),
        ForeignKeyConstraint(['userId'], ['User.id'], ondelete='CASCADE', onupdate='CASCADE', name='ProjectMember_userId_fkey'),
        PrimaryKeyConstraint('id', name='ProjectMember_pkey'),
        Index('ProjectMember_projectId_idx', 'projectId'),
        Index('ProjectMember_projectId_userId_key', 'projectId', 'userId', unique=True),
        Index('ProjectMember_userId_idx', 'userId')
    )

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    projectId: Mapped[str] = mapped_column(Text, nullable=False)
    userId: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(Enum('OWNER', 'ADMIN', 'MEMBER', 'VIEWER', name='ProjectRole'), nullable=False, server_default=text('\'MEMBER\'::"ProjectRole"'))
    joinedAt: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    Project_: Mapped['Project'] = relationship('Project', back_populates='ProjectMember')
    User_: Mapped['User'] = relationship('User', back_populates='ProjectMember')


class Task(Base):
    __tablename__ = 'Task'
    __table_args__ = (
        ForeignKeyConstraint(['assigneeId'], ['User.id'], ondelete='SET NULL', onupdate='CASCADE', name='Task_assigneeId_fkey'),
        ForeignKeyConstraint(['creatorId'], ['User.id'], ondelete='RESTRICT', onupdate='CASCADE', name='Task_creatorId_fkey'),
        ForeignKeyConstraint(['projectId'], ['Project.id'], ondelete='CASCADE', onupdate='CASCADE', name='Task_projectId_fkey'),
        PrimaryKeyConstraint('id', name='Task_pkey'),
        Index('Task_assigneeId_idx', 'assigneeId'),
        Index('Task_creatorId_idx', 'creatorId'),
        Index('Task_dueDate_idx', 'dueDate'),
        Index('Task_projectId_status_idx', 'projectId', 'status')
    )

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Enum('TODO', 'IN_PROGRESS', 'IN_REVIEW', 'DONE', name='TaskStatus'), nullable=False, server_default=text('\'TODO\'::"TaskStatus"'))
    priority: Mapped[str] = mapped_column(Enum('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='TaskPriority'), nullable=False, server_default=text('\'MEDIUM\'::"TaskPriority"'))
    projectId: Mapped[str] = mapped_column(Text, nullable=False)
    creatorId: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text('0'))
    createdAt: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updatedAt: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    assigneeId: Mapped[Optional[str]] = mapped_column(Text)
    dueDate: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=3))

    User_: Mapped[Optional['User']] = relationship('User', foreign_keys=[assigneeId], back_populates='Task')
    User1: Mapped['User'] = relationship('User', foreign_keys=[creatorId], back_populates='Task_')
    Project_: Mapped['Project'] = relationship('Project', back_populates='Task')
    Activity: Mapped[list['Activity']] = relationship('Activity', back_populates='Task_')
    Comment: Mapped[list['Comment']] = relationship('Comment', back_populates='Task_')
    TaskTag: Mapped[list['TaskTag']] = relationship('TaskTag', back_populates='Task_')


class Activity(Base):
    __tablename__ = 'Activity'
    __table_args__ = (
        ForeignKeyConstraint(['projectId'], ['Project.id'], ondelete='SET NULL', onupdate='CASCADE', name='Activity_projectId_fkey'),
        ForeignKeyConstraint(['taskId'], ['Task.id'], ondelete='SET NULL', onupdate='CASCADE', name='Activity_taskId_fkey'),
        ForeignKeyConstraint(['userId'], ['User.id'], ondelete='RESTRICT', onupdate='CASCADE', name='Activity_userId_fkey'),
        PrimaryKeyConstraint('id', name='Activity_pkey'),
        Index('Activity_createdAt_idx', 'createdAt'),
        Index('Activity_projectId_idx', 'projectId'),
        Index('Activity_taskId_idx', 'taskId'),
        Index('Activity_userId_idx', 'userId')
    )

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    userId: Mapped[str] = mapped_column(Text, nullable=False)
    createdAt: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    projectId: Mapped[Optional[str]] = mapped_column(Text)
    taskId: Mapped[Optional[str]] = mapped_column(Text)
    metadata_: Mapped[Optional[dict]] = mapped_column('metadata', JSONB)

    Project_: Mapped[Optional['Project']] = relationship('Project', back_populates='Activity')
    Task_: Mapped[Optional['Task']] = relationship('Task', back_populates='Activity')
    User_: Mapped['User'] = relationship('User', back_populates='Activity')


class Comment(Base):
    __tablename__ = 'Comment'
    __table_args__ = (
        ForeignKeyConstraint(['authorId'], ['User.id'], ondelete='RESTRICT', onupdate='CASCADE', name='Comment_authorId_fkey'),
        ForeignKeyConstraint(['taskId'], ['Task.id'], ondelete='CASCADE', onupdate='CASCADE', name='Comment_taskId_fkey'),
        PrimaryKeyConstraint('id', name='Comment_pkey'),
        Index('Comment_authorId_idx', 'authorId'),
        Index('Comment_taskId_idx', 'taskId')
    )

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    taskId: Mapped[str] = mapped_column(Text, nullable=False)
    authorId: Mapped[str] = mapped_column(Text, nullable=False)
    createdAt: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updatedAt: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), nullable=False)

    User_: Mapped['User'] = relationship('User', back_populates='Comment')
    Task_: Mapped['Task'] = relationship('Task', back_populates='Comment')


class TaskTag(Base):
    __tablename__ = 'TaskTag'
    __table_args__ = (
        ForeignKeyConstraint(['tagId'], ['Tag.id'], ondelete='CASCADE', onupdate='CASCADE', name='TaskTag_tagId_fkey'),
        ForeignKeyConstraint(['taskId'], ['Task.id'], ondelete='CASCADE', onupdate='CASCADE', name='TaskTag_taskId_fkey'),
        PrimaryKeyConstraint('id', name='TaskTag_pkey'),
        Index('TaskTag_tagId_idx', 'tagId'),
        Index('TaskTag_taskId_idx', 'taskId'),
        Index('TaskTag_taskId_tagId_key', 'taskId', 'tagId', unique=True)
    )

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    taskId: Mapped[str] = mapped_column(Text, nullable=False)
    tagId: Mapped[str] = mapped_column(Text, nullable=False)
    createdAt: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(precision=3), nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    Tag_: Mapped['Tag'] = relationship('Tag', back_populates='TaskTag')
    Task_: Mapped['Task'] = relationship('Task', back_populates='TaskTag')
