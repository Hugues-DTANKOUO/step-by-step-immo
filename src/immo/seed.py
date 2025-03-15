"""Script d'initialisation de la base de données avec des données de base."""

import asyncio
import logging

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from immo.config import settings
from immo.extensions import get_db, init_db
from immo.users.models import Permission, Role, User, role_permission, user_role
from immo.utils.models import City, Country, Currency, StatusProject


logger = logging.getLogger(__name__)


async def create_super_admin(db: AsyncSession) -> User:
    """Créer le super administrateur."""
    # Vérifier si le super admin existe déjà
    result = await db.execute(select(User).where(User.email == settings.super_admin["email"]))
    super_admin = result.scalar_one_or_none()

    if super_admin:
        logger.info(f"Super admin already exists: {super_admin.username}")
        return super_admin

    # Créer le super admin
    super_admin = User(
        id=1,
        username=settings.super_admin["username"],
        email=settings.super_admin["email"],
        email_confirmed=settings.super_admin["email_confirmed"],
        first_name=settings.super_admin["first_name"],
        last_name=settings.super_admin["last_name"],
        about_me=settings.super_admin["about_me"],
        terms_confirmation=settings.super_admin["terms_confirmation"],
    )

    # Définir le mot de passe du super admin
    super_admin.set_password(settings.super_admin["password"])

    db.add(super_admin)
    await db.commit()
    await db.refresh(super_admin)

    logger.info(f"Super admin created: {super_admin.username}")
    return super_admin


async def create_roles(db: AsyncSession) -> list[Role]:
    """Créer les rôles de base."""
    roles = [
        Role(id=1, name="SuperAdmin", description="Super administrateur"),
        Role(id=2, name="Admin", description="Administrateur"),
        Role(id=3, name="User", description="Utilisateur"),
        Role(id=4, name="Professionnel", description="Prestataire"),
    ]

    existing_roles = []
    for role in roles:
        # Vérifier si le rôle existe déjà
        result = await db.execute(select(Role).where(Role.id == role.id))
        existing_role = result.scalar_one_or_none()

        if existing_role:
            existing_roles.append(existing_role)
            logger.info(f"Role already exists: {existing_role.name}")
        else:
            db.add(role)
            existing_roles.append(role)
            logger.info(f"Role created: {role.name}")

    await db.commit()

    # Rafraîchir tous les rôles pour obtenir leurs IDs
    for role in existing_roles:
        await db.refresh(role)

    return existing_roles


async def create_permissions(db: AsyncSession) -> list[Permission]:
    """Créer les permissions de base."""
    permissions = [
        Permission(id=1, name="CreateUser", description="Créer un utilisateur"),
        Permission(id=2, name="CreateProject", description="Créer un projet"),
        Permission(id=3, name="CreateService", description="Créer un service"),
        Permission(id=4, name="ReadUser", description="Lire un utilisateur"),
        Permission(id=5, name="ReadProject", description="Lire un projet"),
        Permission(id=6, name="ReadService", description="Lire un service"),
        Permission(id=7, name="UpdateUser", description="Modifier un utilisateur"),
        Permission(id=8, name="UpdateProject", description="Modifier un projet"),
        Permission(id=9, name="UpdateService", description="Modifier un service"),
        Permission(id=10, name="DeleteUser", description="Supprimer un utilisateur"),
        Permission(id=11, name="DeleteProject", description="Supprimer un projet"),
        Permission(id=12, name="DeleteService", description="Supprimer un service"),
        Permission(id=13, name="ListUser", description="Lister les utilisateurs"),
        Permission(id=14, name="ListProject", description="Lister les projets"),
        Permission(id=15, name="ListService", description="Lister les services"),
        Permission(id=16, name="ListAllProject", description="Lister tous les projets"),
        Permission(id=17, name="ListAllService", description="Lister tous les services"),
        Permission(id=18, name="CreateRole", description="Créer un rôle"),
        Permission(id=19, name="ReadRole", description="Lire un rôle"),
        Permission(id=20, name="UpdateRole", description="Modifier un rôle"),
        Permission(id=21, name="DeleteRole", description="Supprimer un rôle"),
        Permission(id=22, name="ListRole", description="Lister les rôles"),
        Permission(id=23, name="CreatePermission", description="Créer une permission"),
        Permission(id=24, name="ReadPermission", description="Lire une permission"),
        Permission(id=25, name="UpdatePermission", description="Modifier une permission"),
        Permission(id=26, name="DeletePermission", description="Supprimer une permission"),
        Permission(id=27, name="ListPermission", description="Lister les permissions"),
        Permission(id=28, name="CreateUserRole", description="Créer un rôle d'utilisateur"),
        Permission(id=29, name="ReadUserRole", description="Lire un rôle d'utilisateur"),
        Permission(id=30, name="UpdateUserRole", description="Modifier un rôle d'utilisateur"),
        Permission(id=31, name="DeleteUserRole", description="Supprimer un rôle d'utilisateur"),
        Permission(id=32, name="ListUserRole", description="Lister les rôles d'utilisateurs"),
        Permission(id=33, name="CreateRolePermission", description="Créer une permission de rôle"),
        Permission(id=34, name="ReadRolePermission", description="Lire une permission de rôle"),
        Permission(id=35, name="UpdateRolePermission", description="Modifier une permission de rôle"),
        Permission(id=36, name="DeleteRolePermission", description="Supprimer une permission de rôle"),
        Permission(id=37, name="ListRolePermission", description="Lister les permissions de rôles"),
        Permission(id=38, name="CreateMoreThanFiveProject", description="Créer plus de cinq projets"),
        Permission(id=39, name="CreateMoreThanFiveService", description="Créer plus de cinq services"),
        Permission(id=40, name="CreateCountry", description="Créer un pays"),
        Permission(id=41, name="ReadCountry", description="Lire un pays"),
        Permission(id=42, name="UpdateCountry", description="Modifier un pays"),
        Permission(id=43, name="DeleteCountry", description="Supprimer un pays"),
        Permission(id=44, name="ListCountry", description="Lister les pays"),
        Permission(id=45, name="CreateCity", description="Créer une ville"),
        Permission(id=46, name="ReadCity", description="Lire une ville"),
        Permission(id=47, name="UpdateCity", description="Modifier une ville"),
        Permission(id=48, name="DeleteCity", description="Supprimer une ville"),
        Permission(id=49, name="ListCity", description="Lister les villes"),
        Permission(id=50, name="CreateCurrency", description="Créer une devise"),
        Permission(id=51, name="ReadCurrency", description="Lire une devise"),
        Permission(id=52, name="UpdateCurrency", description="Modifier une devise"),
        Permission(id=53, name="DeleteCurrency", description="Supprimer une devise"),
        Permission(id=54, name="ListCurrency", description="Lister les devises"),
        Permission(id=55, name="CreateStatusProject", description="Créer un status de projet"),
        Permission(id=56, name="ReadStatusProject", description="Lire un status de projet"),
        Permission(id=57, name="UpdateStatusProject", description="Modifier un status de projet"),
        Permission(id=58, name="DeleteStatusProject", description="Supprimer un status de projet"),
        Permission(id=59, name="ListStatusProject", description="Lister les status de projets"),
        Permission(id=60, name="CreateOtherUser", description="Créer un autre utilisateur"),
        Permission(id=61, name="ReadOtherUser", description="Lire un autre utilisateur"),
        Permission(id=62, name="UpdateOtherUser", description="Modifier un autre utilisateur"),
        Permission(id=63, name="DeleteOtherUser", description="Supprimer un autre utilisateur"),
        Permission(id=64, name="CreateOtherProject", description="Créer un autre projet"),
        Permission(id=65, name="ReadOtherProject", description="Lire un autre projet"),
        Permission(id=66, name="UpdateOtherProject", description="Modifier un autre projet"),
        Permission(id=67, name="DeleteOtherProject", description="Supprimer un autre projet"),
        Permission(id=68, name="CreateOtherService", description="Créer un autre service"),
        Permission(id=69, name="ReadOtherService", description="Lire un autre service"),
        Permission(id=70, name="UpdateOtherService", description="Modifier un autre service"),
        Permission(id=71, name="DeleteOtherService", description="Supprimer un autre service"),
        Permission(id=72, name="ListOtherProject", description="Lister les autres projets"),
        Permission(id=73, name="ListOtherService", description="Lister les autres services"),
        Permission(id=74, name="CreateStep", description="Créer une étape"),
        Permission(id=75, name="ReadStep", description="Lire une étape"),
        Permission(id=76, name="UpdateStep", description="Modifier une étape"),
        Permission(id=77, name="DeleteStep", description="Supprimer une étape"),
        Permission(id=78, name="ListStep", description="Lister les étapes"),
        Permission(id=79, name="CreateOtherStep", description="Créer une autre étape"),
        Permission(id=80, name="ReadOtherStep", description="Lire une autre étape"),
        Permission(id=81, name="UpdateOtherStep", description="Modifier une autre étape"),
        Permission(id=82, name="DeleteOtherStep", description="Supprimer une autre étape"),
        Permission(id=83, name="ListOtherStep", description="Lister les autres étapes"),
        Permission(id=84, name="CreateMoreThanFiveStep", description="Créer plus de cinq étapes"),
        Permission(id=85, name="CreateAdmin", description="Créer un administrateur"),
        Permission(id=86, name="ReadAdmin", description="Lire un administrateur"),
        Permission(id=87, name="UpdateAdmin", description="Modifier un administrateur"),
        Permission(id=88, name="DeleteAdmin", description="Supprimer un administrateur"),
    ]

    # Sous-ensemble des permissions pour les utilisateurs standard
    user_permissions_ids = [1, 2, 3, 4, 5, 7, 8, 11, 13, 14, 15, 16, 17, 59, 74, 75, 76, 77, 78]

    existing_permissions = []
    for permission in permissions:
        # Vérifier si la permission existe déjà
        result = await db.execute(select(Permission).where(Permission.id == permission.id))
        existing_permission = result.scalar_one_or_none()

        if existing_permission:
            existing_permissions.append(existing_permission)
            logger.info(f"Permission already exists: {existing_permission.name}")
        else:
            db.add(permission)
            existing_permissions.append(permission)
            logger.info(f"Permission created: {permission.name}")

    await db.commit()

    # Rafraîchir toutes les permissions pour obtenir leurs IDs
    for permission in existing_permissions:
        await db.refresh(permission)

    return existing_permissions, user_permissions_ids


async def assign_super_admin_role(db: AsyncSession, super_admin: User, roles: list[Role]) -> None:
    """Assigner le rôle de super administrateur au super admin."""
    # Vérifier si le rôle est déjà assigné
    result = await db.execute(
        select(user_role).where(
            user_role.c.user_id == super_admin.id,
            user_role.c.role_id == 1,  # SuperAdmin role_id
        )
    )

    if result.scalar_one_or_none():
        logger.info(f"SuperAdmin role already assigned to: {super_admin.username}")
        return

    # Ajouter le rôle SuperAdmin
    await db.execute(
        insert(user_role).values(
            user_id=super_admin.id,
            role_id=1,  # SuperAdmin role_id
        )
    )

    await db.commit()
    logger.info(f"SuperAdmin role assigned to: {super_admin.username}")


async def assign_role_permissions(
    db: AsyncSession, roles: list[Role], permissions: list[Permission], user_permissions_ids: list[int]
) -> None:
    """Assigner les permissions aux rôles."""
    # Permissions pour SuperAdmin (toutes les permissions)
    for permission in permissions:
        # Vérifier si la permission est déjà assignée
        result = await db.execute(
            select(role_permission).where(
                role_permission.c.role_id == 1,  # SuperAdmin role_id
                role_permission.c.permission_id == permission.id,
            )
        )

        if not result.scalar_one_or_none():
            await db.execute(
                insert(role_permission).values(
                    role_id=1,  # SuperAdmin role_id
                    permission_id=permission.id,
                )
            )
            logger.info(f"Permission {permission.name} assigned to SuperAdmin role")

    # Permissions pour Admin (toutes les permissions sauf les dernières spécifiques au SuperAdmin)
    for permission in permissions:
        if permission.id < 85:  # Exclure les permissions spécifiques au SuperAdmin
            # Vérifier si la permission est déjà assignée
            result = await db.execute(
                select(role_permission).where(
                    role_permission.c.role_id == 2,  # Admin role_id
                    role_permission.c.permission_id == permission.id,
                )
            )

            if not result.scalar_one_or_none():
                await db.execute(
                    insert(role_permission).values(
                        role_id=2,  # Admin role_id
                        permission_id=permission.id,
                    )
                )
                logger.info(f"Permission {permission.name} assigned to Admin role")

    # Permissions pour User (permissions de base)
    for permission_id in user_permissions_ids:
        # Vérifier si la permission est déjà assignée
        result = await db.execute(
            select(role_permission).where(
                role_permission.c.role_id == 3,  # User role_id
                role_permission.c.permission_id == permission_id,
            )
        )

        if not result.scalar_one_or_none():
            await db.execute(
                insert(role_permission).values(
                    role_id=3,  # User role_id
                    permission_id=permission_id,
                )
            )
            logger.info(f"Permission {permission_id} assigned to User role")

    await db.commit()


async def create_countries(db: AsyncSession, super_admin_id: int) -> list[Country]:
    """Créer les pays de base."""
    countries = [
        Country(id=1, name="Cameroun", code="CM", created_by=super_admin_id),
        Country(id=2, name="Bénin", code="BJ", created_by=super_admin_id),
        Country(id=3, name="Burkina Faso", code="BF", created_by=super_admin_id),
        Country(id=4, name="Côte d'Ivoire", code="CI", created_by=super_admin_id),
        Country(id=5, name="Gabon", code="GA", created_by=super_admin_id),
        Country(id=6, name="Guinée", code="GN", created_by=super_admin_id),
        Country(id=7, name="Mali", code="ML", created_by=super_admin_id),
        Country(id=8, name="Niger", code="NE", created_by=super_admin_id),
        Country(id=9, name="Sénégal", code="SN", created_by=super_admin_id),
        Country(id=10, name="Togo", code="TG", created_by=super_admin_id),
        Country(id=11, name="France", code="FR", created_by=super_admin_id),
        Country(id=12, name="Belgique", code="BE", created_by=super_admin_id),
        Country(id=13, name="Allemagne", code="DE", created_by=super_admin_id),
        Country(id=14, name="Italie", code="IT", created_by=super_admin_id),
        Country(id=15, name="Angleterre", code="GB", created_by=super_admin_id),
        Country(id=16, name="Canada", code="CA", created_by=super_admin_id),
        Country(id=17, name="Suisse", code="CH", created_by=super_admin_id),
        Country(id=18, name="États-Unis", code="US", created_by=super_admin_id),
        Country(id=19, name="Congo-Brazzaville", code="CG", created_by=super_admin_id),
        Country(id=20, name="Congo-Kinshasa", code="CD", created_by=super_admin_id),
        Country(id=21, name="Tchad", code="TD", created_by=super_admin_id),
        Country(id=22, name="Autre", code="XX", created_by=super_admin_id),
    ]

    existing_countries = []
    for country in countries:
        # Vérifier si le pays existe déjà
        result = await db.execute(select(Country).where(Country.id == country.id))
        existing_country = result.scalar_one_or_none()

        if existing_country:
            existing_countries.append(existing_country)
            logger.info(f"Country already exists: {existing_country.name}")
        else:
            db.add(country)
            existing_countries.append(country)
            logger.info(f"Country created: {country.name}")

    await db.commit()

    # Rafraîchir tous les pays pour obtenir leurs IDs
    for country in existing_countries:
        await db.refresh(country)

    return existing_countries


async def create_cities(db: AsyncSession, super_admin_id: int) -> None:
    """Créer les villes de base."""
    # Une liste partielle des villes pour l'exemple
    cities = [
        City(id=1, name="Douala", country_id=1, created_by=super_admin_id),
        City(id=2, name="Yaoundé", country_id=1, created_by=super_admin_id),
        City(id=3, name="Bafoussam", country_id=1, created_by=super_admin_id),
        City(id=4, name="Kribi", country_id=1, created_by=super_admin_id),
        City(id=5, name="Limbe", country_id=1, created_by=super_admin_id),
        City(id=6, name="Cotonou", country_id=2, created_by=super_admin_id),
        City(id=7, name="Porto-Novo", country_id=2, created_by=super_admin_id),
        City(id=8, name="Parakou", country_id=2, created_by=super_admin_id),
        City(id=9, name="Natitingou", country_id=2, created_by=super_admin_id),
        City(id=10, name="Ouagadougou", country_id=3, created_by=super_admin_id),
        City(id=11, name="Bobo-Dioulasso", country_id=3, created_by=super_admin_id),
        City(id=12, name="Banfora", country_id=3, created_by=super_admin_id),
        City(id=13, name="Koudougou", country_id=3, created_by=super_admin_id),
        # Ajoutez plus de villes selon vos besoins
    ]

    for city in cities:
        # Vérifier si la ville existe déjà
        result = await db.execute(select(City).where(City.id == city.id))
        existing_city = result.scalar_one_or_none()

        if existing_city:
            logger.info(f"City already exists: {existing_city.name}")
        else:
            db.add(city)
            logger.info(f"City created: {city.name}")

    await db.commit()


async def create_currencies(db: AsyncSession, super_admin_id: int) -> None:
    """Créer les devises de base."""
    currencies = [
        Currency(id=1, name="Franc CFA", code="XAF", created_by=super_admin_id),
        Currency(id=2, name="Euro", code="EUR", created_by=super_admin_id),
        Currency(id=3, name="Dollar américain", code="USD", created_by=super_admin_id),
        Currency(id=4, name="Livre sterling", code="GBP", created_by=super_admin_id),
        Currency(id=5, name="Franc suisse", code="CHF", created_by=super_admin_id),
        Currency(id=6, name="Dollar canadien", code="CAD", created_by=super_admin_id),
        Currency(id=7, name="Franc congolais", code="CDF", created_by=super_admin_id),
        Currency(id=8, name="Franc guinéen", code="GNF", created_by=super_admin_id),
        Currency(id=9, name="Franc malien", code="XOF", created_by=super_admin_id),
    ]

    for currency in currencies:
        # Vérifier si la devise existe déjà
        result = await db.execute(select(Currency).where(Currency.id == currency.id))
        existing_currency = result.scalar_one_or_none()

        if existing_currency:
            logger.info(f"Currency already exists: {existing_currency.name}")
        else:
            db.add(currency)
            logger.info(f"Currency created: {currency.name}")

    await db.commit()


async def create_status_projects(db: AsyncSession) -> None:
    """Créer les statuts de projet de base."""
    status_projects = [
        StatusProject(id=1, name="En cours", description="Projet en cours"),
        StatusProject(id=2, name="Terminé", description="Projet terminé"),
        StatusProject(id=3, name="Annulé", description="Projet annulé"),
    ]

    for status_project in status_projects:
        # Vérifier si le statut de projet existe déjà
        result = await db.execute(select(StatusProject).where(StatusProject.id == status_project.id))
        existing_status_project = result.scalar_one_or_none()

        if existing_status_project:
            logger.info(f"Status project already exists: {existing_status_project.name}")
        else:
            db.add(status_project)
            logger.info(f"Status project created: {status_project.name}")

    await db.commit()


async def seed_database() -> None:
    """Initialiser la base de données avec des données de base."""
    # Initialiser la connexion à la base de données
    await init_db()

    async for db in get_db():
        try:
            # Créer le super administrateur
            super_admin = await create_super_admin(db)

            # Créer les rôles
            roles = await create_roles(db)

            # Créer les permissions
            permissions, user_permissions_ids = await create_permissions(db)

            # Assigner le rôle de super administrateur
            await assign_super_admin_role(db, super_admin, roles)

            # Assigner les permissions aux rôles
            await assign_role_permissions(db, roles, permissions, user_permissions_ids)

            # Créer les pays
            countries = await create_countries(db, super_admin.id)

            # Créer les villes
            await create_cities(db, super_admin.id)

            # Créer les devises
            await create_currencies(db, super_admin.id)

            # Créer les statuts de projet
            await create_status_projects(db)

            logger.info("Database seeded successfully!")
            break

        except Exception as e:
            logger.error(f"Error seeding database: {e}")
            raise e


if __name__ == "__main__":
    # Configurer le logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Exécuter l'initialisation de la base de données
    asyncio.run(seed_database())
