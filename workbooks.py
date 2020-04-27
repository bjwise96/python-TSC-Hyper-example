import logging
import csv
import tableauserverclient as TSC
import yaml
from pathlib import Path
from tableauhyperapi import HyperProcess, Telemetry, \
    Connection, CreateMode, \
    NOT_NULLABLE, NULLABLE, SqlType, TableDefinition, \
    Inserter, \
    escape_name, escape_string_literal, \
    HyperException

#Create table definition to be used in Hyper file
workbook_table = TableDefinition(
    table_name="Workbooks",
    columns=[
        TableDefinition.Column("Project Id", SqlType.text(), NOT_NULLABLE),
        TableDefinition.Column(
            "Content URL", SqlType.text(), NOT_NULLABLE),
        TableDefinition.Column("Created At", SqlType.date(), NOT_NULLABLE),
        TableDefinition.Column("Id", SqlType.text(), NOT_NULLABLE),
        TableDefinition.Column(
            "Project Name", SqlType.text(), NOT_NULLABLE),
        TableDefinition.Column("size", SqlType.big_int(), NOT_NULLABLE),
        TableDefinition.Column("Updated At", SqlType.date(), NOT_NULLABLE),
        TableDefinition.Column("Name", SqlType.text(), NOT_NULLABLE)
    ]
)
#Name of hyper file that will be generated locally and deployed to Tableau
path_to_database = Path("workbooks.hyper")
#Name of project where Hyper file will be deployed
#This project must exist on your server
PROJECT = 'HyperTest'


def main():

    #Read in environment variables necessary to make connection
    with open('env.yaml') as f:
        env = yaml.load(f, Loader=yaml.FullLoader)

    tableau_auth = TSC.PersonalAccessTokenAuth(
        token_name=env["PATNAME"], personal_access_token=env["PAT"], site_id=env["SITE"])
    server = TSC.Server(env["SERVER"])

    with server.auth.sign_in(tableau_auth):

        #Get all workbooks
        all_workbooks = list(TSC.Pager(server.workbooks))

        #Write this to CSV
        with open('workbooks.csv', 'w',) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Project Id', 'Content URL', 'Created At',
                             'Id', 'Project Name', 'Size', 'Updated At', 'Name'])
            for workbook in all_workbooks:
                writer.writerow([workbook.project_id, workbook.content_url, workbook.created_at,
                                 workbook.id, workbook.project_name, workbook.size, workbook.updated_at, workbook.name])

        #Copy CSV into Hyper file
        with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
            with Connection(endpoint=hyper.endpoint,
                            database=path_to_database,
                            create_mode=CreateMode.CREATE_AND_REPLACE) as connection:
                connection.catalog.create_table(
                    table_definition=workbook_table)
                path_to_csv = str(Path(__file__).parent / "workbooks.csv")
                count_in_workbook_table = connection.execute_command(
                    command=f"COPY {workbook_table.table_name} from {escape_string_literal(path_to_csv)} with "
                    f"(format csv, NULL 'NULL', delimiter ',', header)")
                print(
                    f"The number of rows in table {workbook_table.table_name} is {count_in_workbook_table}.")

        #Deploye Hyper file to server
        all_projects, pagination_item = server.projects.get()
        all_projects_name = [proj.name for proj in all_projects]
        # if default project is found, publish (and overwrite) a new datasource.
        if PROJECT in all_projects_name:
            PROJECT_ID = all_projects_name.index(PROJECT)
            default_project = all_projects[PROJECT_ID]
            print(f"Publish data extract in {default_project.name} project")
            new_extract = TSC.DatasourceItem(
                project_id=default_project.id, name="Workbooks Hyper File")
            new_extract = server.datasources.publish(datasource_item=new_extract,
                                                    file_path=path_to_database,
                                                    mode=TSC.Server.PublishMode.Overwrite)
            print(f"Extract published. ID: {new_extract.id}")
        else:
            error = "The default project could not be found."
            raise LookupError(error)


if __name__ == '__main__':
    main()
