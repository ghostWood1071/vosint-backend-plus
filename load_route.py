from app.auth.routers import router as AuthRouter
from app.dashboard.router import router as DashboardRouter
from app.event.router import router as EventRouter
from app.information.route import router as InformationRouter
from app.list_object.route import router as ObjectRouter
from app.manage_news.route import router as ManageNewsRouter
from app.news.routers import router as NewsRouter
from app.newsletter.routers import router as NewsLetterRouter
from app.proxy.route import router as ProxyRouter
from app.report.router import router as ReportRouter
from app.social.routers import router as SocialRouter
from app.social_media.routers import router as SocialMediaRouter
from app.upload.upload_file import router as UploadFileRouter
from app.user.routers import router as UserRouter
from app.user_config.router import router as UserConfigRouter
from app.vnanet.vn_new import router as VNNewRouter
from vosint_ingestion.features.job.routers import router as Job
from app.resource_monitor.routers import router as ResourceMonitorRouter
from app.slave_activity.routers import router as SlaveActivityRouter
from app.email.routers import router as EmailRouter

# from vosint_ingestion.features.nlp.routers import router as Nlp
from vosint_ingestion.features.pipeline.routers import router as PipeLine
from app.nlp.routers import router as NLPRouter

from app.role.routers import router as RoleRouter
from app.branch.routers import router as BranchRouter
from app.department.routers import router as DepartmentRouter
from app.action.routers import router as ActionRouter
from app.function.routers import router as FunctionRouter
from app.role_function.routers import router as RoleFunctionRouter
from app.role_permission.routers import router as RolePermissionRouter
from app.catalog.routers import router as CatalogRouter
from app.hislog.router import router as HisLogRouter
from app.data_manager.router import router as DataRouter
from app.dictionary.router import router as DictionaryRouter

ROUTE_LIST = [
    {"route": AuthRouter, "tags": ["Xác Thực"], "prefix": ""},
    {"route": UserRouter, "tags": ["User"], "prefix": "/user"},
    {"route": NewsLetterRouter, "tags": ["NewsLetters"], "prefix": "/newsletters"},
    {"route": NewsRouter, "tags": ["News"], "prefix": "/news"},
    {"route": UploadFileRouter, "tags": ["Upload"], "prefix": "/upload"},
    {"route": ObjectRouter, "tags": ["Object"], "prefix": "/object"},
    {"route": Job, "tags": ["Job"], "prefix": "/Job"},
    {"route": PipeLine, "tags": ["Pipeline"], "prefix": "/Pipeline"},
    {"route": NLPRouter, "tags": ["NLP"], "prefix": "/nlp"},
    {"route": ProxyRouter, "tags": ["Proxy"], "prefix": "/Proxy"},
    {"route": InformationRouter, "tags": ["Source"], "prefix": "/Source"},
    {
        "route": ManageNewsRouter,
        "tags": ["Source-group"],
        "prefix": "/Source-group",
    },
    {
        "route": SocialMediaRouter,
        "tags": ["Social-media"],
        "prefix": "/Social-media",
    },
    {"route": SocialRouter, "tags": ["Social"], "prefix": "/account-monitor"},
    {"route": EventRouter, "tags": ["Event"], "prefix": "/event"},
    {"route": ReportRouter, "tags": ["Report"], "prefix": "/report"},
    {"route": VNNewRouter, "tags": ["VNNew"], "prefix": "/vnnew"},
    {
        "route": UserConfigRouter,
        "tags": ["Account ttxvn config"],
        "prefix": "/account-ttxvn-config",
    },
    {
        "route": ResourceMonitorRouter,
        "tags": ["ResourceMonitor"],
        "prefix": "/resource-monitor",
    },
    {
        "route": SlaveActivityRouter,
        "tags": ["SlaveActivity"],
        "prefix": "/slave-activity",
    },
    {"route": DashboardRouter, "tags": ["Dashboard"], "prefix": "/dashboard"},

    {"route": RoleRouter, "tags": ["Role"], "prefix": "/role"},
    {"route": BranchRouter, "tags": ["Branch"], "prefix": "/branch"},
    {"route": DepartmentRouter, "tags": ["Department"], "prefix": "/department"},
    {"route": ActionRouter, "tags": ["Action"], "prefix": "/action"},
    {"route": FunctionRouter, "tags": ["Function"], "prefix": "/function"},
    {"route": RoleFunctionRouter, "tags": ["RoleFunction"], "prefix": "/role-function"},
    {"route": RolePermissionRouter, "tags": ["RolePermission"], "prefix": "/role-permission"},
    {"route": EmailRouter, "tags": ["Email"], "prefix": "/email"},
    {"route": CatalogRouter, "tags": ["Catalog"], "prefix": "/catalog"},
    {"route": HisLogRouter, "tags": ["History Log"], "prefix": "/hislog"},
    {"route": DataRouter, "tags": ["Kho du lieu"], "prefix": "/data"}, 
    {"route": DictionaryRouter, "tags": ["Tu dien"], "prefix": "/dictionary"}
]
